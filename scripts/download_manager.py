from __future__ import annotations

from pathlib import Path
from datetime import datetime
import shutil
import logging
import yaml

BASE_DIR = Path.home() / "Projects" / "personal-mac-automation"
CONFIG_FILE = BASE_DIR / "configs" / "download-rules.yaml"

def expand_path(value: str) -> Path:
    return Path(value).expanduser()

def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

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

def safe_move(src: Path, dst_dir: Path, dry_run: bool) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name

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

def route_file(item: Path, config: dict, dry_run: bool) -> None:
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

    if route == "review":
        safe_move(item, expand_path(paths["to_review_dir"]), dry_run)
        return

    age = file_age_days(item)

    archive_after_days = rule.get("archive_after_days")
    trash_after_days = rule.get("trash_after_days")
    delete_after_days = rule.get("delete_after_days")

    if archive_after_days is not None and age >= archive_after_days:
        safe_move(item, expand_path(paths["auto_archive_dir"]), dry_run)
        return

    if trash_after_days is not None and age >= trash_after_days:
        safe_move(item, expand_path(paths["trash_later_dir"]), dry_run)
        return

    if delete_after_days is not None and age >= delete_after_days:
        safe_delete(item, dry_run)
        return

    logging.info("NO ACTION %s ext=%s age_days=%.2f", item, ext, age)

def process_folder(source_dir: Path, config: dict, dry_run: bool) -> None:
    if not source_dir.exists():
        return

    for item in source_dir.iterdir():
        if not item.is_file():
            continue

        route_file(item, config, dry_run)

def main() -> None:
    config = load_config()
    paths = config["paths"]
    dry_run = config.get("settings", {}).get("dry_run", True)

    downloads_dir = expand_path(paths["downloads_dir"])
    log_file = expand_path(paths["log_file"])

    setup_logging(log_file)
    logging.info("Download manager started. dry_run=%s", dry_run)

    process_folder(downloads_dir, config, dry_run)

    logging.info("Download manager finished.")

if __name__ == "__main__":
    main()
