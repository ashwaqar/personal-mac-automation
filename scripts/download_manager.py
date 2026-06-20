from __future__ import annotations

import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

BASE_DIR = Path.home() / "Projects" / "personal-mac-automation"
CONFIG_FILE = Path(
    os.environ.get("DOWNLOAD_RULES_CONFIG", str(BASE_DIR / "configs" / "download-rules.yaml"))
)


def expand_path(value: str) -> Path:
    return Path(value).expanduser()


def load_config() -> dict:
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Config file not found: %s", CONFIG_FILE)
        sys.exit(1)
    except yaml.YAMLError as exc:
        logging.error("Invalid YAML in config: %s", exc)
        sys.exit(1)

    if not isinstance(config, dict):
        logging.error("Config must be a YAML mapping")
        sys.exit(1)

    return config


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def file_age_days(path: Path) -> float:
    return (datetime.now().timestamp() - path.stat().st_mtime) / 86400


def get_extension(item: Path) -> str:
    return item.suffix.lower().lstrip(".")


def get_rule(config: dict, item: Path) -> dict:
    ext = get_extension(item)
    return config.get("rules", {}).get(ext, config.get("default", {}))


def unique_destination(dst_dir: Path, filename: str) -> Path:
    candidate = dst_dir / filename
    if not candidate.exists():
        return candidate

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dst_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def safe_move(src: Path, dst_dir: Path, dry_run: bool) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = unique_destination(dst_dir, src.name)

    if dry_run:
        print(f"Would move: {src} -> {dst}")
        logging.info("DRY_RUN MOVE %s -> %s", src, dst)
        return

    shutil.move(str(src), str(dst))
    print(f"Moved: {src} -> {dst}")
    logging.info("MOVE %s -> %s", src, dst)


def safe_delete(path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"Would delete: {path}")
        logging.info("DRY_RUN DELETE %s", path)
        return

    path.unlink()
    print(f"Deleted: {path}")
    logging.info("DELETE %s", path)


def route_downloads_file(item: Path, config: dict, dry_run: bool) -> None:
    paths = config["paths"]
    rule = get_rule(config, item)
    ext = get_extension(item)
    route = rule.get("route", "archive")

    if route == "media":
        safe_move(item, expand_path(paths["media_incoming_dir"]), dry_run)
        return

    if route == "media_assets":
        safe_move(item, expand_path(paths["media_assets_dir"]), dry_run)
        return

    age = file_age_days(item)
    archive_after_days = rule.get("archive_after_days")

    if route == "review":
        if archive_after_days is not None and age >= archive_after_days:
            safe_move(item, expand_path(paths["to_review_dir"]), dry_run)
        else:
            logging.info("NO ACTION %s ext=%s age_days=%.2f", item, ext, age)
        return

    if archive_after_days is not None and age >= archive_after_days:
        safe_move(item, expand_path(paths["auto_archive_dir"]), dry_run)
    else:
        logging.info("NO ACTION %s ext=%s age_days=%.2f", item, ext, age)


def process_downloads_folder(source_dir: Path, config: dict, dry_run: bool) -> int:
    errors = 0
    if not source_dir.exists():
        return errors

    for item in source_dir.iterdir():
        if not item.is_file():
            continue
        try:
            route_downloads_file(item, config, dry_run)
        except OSError as exc:
            logging.error("Failed to process %s: %s", item, exc)
            errors += 1

    return errors


def process_staged_folder(
    source_dir: Path,
    target_dir: Path,
    threshold_key: str,
    config: dict,
    dry_run: bool,
) -> int:
    errors = 0
    if not source_dir.exists():
        return errors

    for item in source_dir.iterdir():
        if not item.is_file():
            continue

        try:
            rule = get_rule(config, item)
            threshold_days = rule.get(threshold_key)
            if threshold_days is None:
                continue

            age = file_age_days(item)
            if age >= threshold_days:
                if threshold_key == "delete_after_days":
                    safe_delete(item, dry_run)
                else:
                    safe_move(item, target_dir, dry_run)
        except OSError as exc:
            logging.error("Failed to process %s: %s", item, exc)
            errors += 1

    return errors


def main() -> None:
    config = load_config()
    paths = config["paths"]
    dry_run = config.get("settings", {}).get("dry_run", True)

    downloads_dir = expand_path(paths["downloads_dir"])
    auto_archive_dir = expand_path(paths["auto_archive_dir"])
    trash_later_dir = expand_path(paths["trash_later_dir"])
    log_file = expand_path(paths["log_file"])

    setup_logging(log_file)
    logging.info("Download manager started. dry_run=%s", dry_run)

    errors = 0
    errors += process_downloads_folder(downloads_dir, config, dry_run)
    errors += process_staged_folder(
        auto_archive_dir, trash_later_dir, "trash_after_days", config, dry_run
    )
    errors += process_staged_folder(
        trash_later_dir, trash_later_dir, "delete_after_days", config, dry_run
    )

    logging.info("Download manager finished. errors=%d", errors)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
