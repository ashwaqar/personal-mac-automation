from __future__ import annotations

import hashlib
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

REQUIRED_PATHS = (
    "downloads_dir",
    "auto_archive_dir",
    "trash_later_dir",
    "to_review_dir",
    "media_incoming_dir",
    "media_assets_dir",
    "log_file",
)
WORKSPACE_PATH_DIRS = (
    "downloads_dir",
    "auto_archive_dir",
    "trash_later_dir",
    "to_review_dir",
    "media_incoming_dir",
    "media_assets_dir",
)
VALID_ROUTES = frozenset({"media", "media_assets", "review", "archive"})
THRESHOLD_KEYS = ("archive_after_days", "trash_after_days", "delete_after_days")


def expand_path(value: str) -> Path:
    return Path(value).expanduser()


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []

    settings = config.get("settings")
    if settings is not None and not isinstance(settings, dict):
        errors.append("settings must be a mapping")
    elif isinstance(settings, dict):
        if "dry_run" in settings and not isinstance(settings["dry_run"], bool):
            errors.append("settings.dry_run must be a boolean")
        if "duplicate_detection" in settings and not isinstance(
            settings["duplicate_detection"], bool
        ):
            errors.append("settings.duplicate_detection must be a boolean")
        if "bootstrap_folders" in settings and not isinstance(
            settings["bootstrap_folders"], bool
        ):
            errors.append("settings.bootstrap_folders must be a boolean")

    paths = config.get("paths")
    if not isinstance(paths, dict):
        errors.append("paths must be a mapping")
    else:
        for key in REQUIRED_PATHS:
            if key not in paths:
                errors.append(f"paths.{key} is required")
            elif not isinstance(paths[key], str) or not paths[key].strip():
                errors.append(f"paths.{key} must be a non-empty string")

    rules = config.get("rules")
    if rules is not None and not isinstance(rules, dict):
        errors.append("rules must be a mapping")
    elif isinstance(rules, dict):
        for ext, rule in rules.items():
            if not isinstance(rule, dict):
                errors.append(f"rules.{ext} must be a mapping")
                continue
            errors.extend(_validate_rule(rule, f"rules.{ext}"))

    default = config.get("default")
    if default is not None:
        if not isinstance(default, dict):
            errors.append("default must be a mapping")
        else:
            errors.extend(_validate_rule(default, "default"))

    bootstrap_dirs = config.get("bootstrap_dirs")
    if bootstrap_dirs is not None:
        if not isinstance(bootstrap_dirs, list):
            errors.append("bootstrap_dirs must be a list")
        else:
            for index, entry in enumerate(bootstrap_dirs):
                if not isinstance(entry, str) or not entry.strip():
                    errors.append(f"bootstrap_dirs[{index}] must be a non-empty string")

    return errors


def _validate_rule(rule: dict, label: str) -> list[str]:
    errors: list[str] = []
    route = rule.get("route", "archive")

    if route not in VALID_ROUTES:
        errors.append(f"{label}.route must be one of: {', '.join(sorted(VALID_ROUTES))}")

    thresholds: dict[str, int] = {}
    for key in THRESHOLD_KEYS:
        if key not in rule:
            continue
        value = rule[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{label}.{key} must be a non-negative integer")
        else:
            thresholds[key] = value

    ordered = [thresholds[k] for k in THRESHOLD_KEYS if k in thresholds]
    if len(ordered) >= 2 and ordered != sorted(ordered):
        errors.append(f"{label} thresholds must be in ascending order (archive < trash < delete)")

    if route == "review" and "archive_after_days" not in rule:
        errors.append(f"{label} with route: review requires archive_after_days")

    return errors


def load_config() -> dict:
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as exc:
        print(f"Invalid YAML in config: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(config, dict):
        print("Config must be a YAML mapping", file=sys.stderr)
        sys.exit(1)

    return config


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def ensure_directory(path: Path) -> Path | None:
    if path.exists():
        return None
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_workspace(config: dict) -> list[Path]:
    settings = config.get("settings", {})
    if not settings.get("bootstrap_folders", True):
        return []

    paths = config["paths"]
    created: list[Path] = []

    for key in WORKSPACE_PATH_DIRS:
        result = ensure_directory(expand_path(paths[key]))
        if result is not None:
            created.append(result)

    log_dir = expand_path(paths["log_file"]).parent
    result = ensure_directory(log_dir)
    if result is not None:
        created.append(result)

    bootstrap_dirs = config.get("bootstrap_dirs")
    if isinstance(bootstrap_dirs, list):
        for entry in bootstrap_dirs:
            result = ensure_directory(expand_path(entry))
            if result is not None:
                created.append(result)

    return created


def file_age_days(path: Path) -> float:
    return (datetime.now().timestamp() - path.stat().st_mtime) / 86400


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_content_duplicate(src: Path, directory: Path) -> Path | None:
    """Return an existing file with the same name and content, if any."""
    if not directory.exists():
        return None

    candidate = directory / src.name
    if not candidate.is_file() or candidate.resolve() == src.resolve():
        return None

    try:
        if candidate.stat().st_size != src.stat().st_size:
            return None
        if file_hash(candidate) == file_hash(src):
            return candidate
    except OSError:
        return None

    return None


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


def remove_duplicate_source(src: Path, duplicate: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"Would remove duplicate: {src} (matches {duplicate})")
        logging.info("DRY_RUN DUPLICATE %s matches %s", src, duplicate)
        return

    src.unlink()
    print(f"Removed duplicate: {src} (matches {duplicate})")
    logging.info("DUPLICATE %s matches %s", src, duplicate)


def safe_move(
    src: Path,
    dst_dir: Path,
    dry_run: bool,
    *,
    check_duplicates: bool = True,
) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)

    if check_duplicates:
        duplicate = find_content_duplicate(src, dst_dir)
        if duplicate is not None:
            remove_duplicate_source(src, duplicate, dry_run)
            return

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


def route_downloads_file(
    item: Path, config: dict, dry_run: bool, *, check_duplicates: bool
) -> None:
    paths = config["paths"]
    rule = get_rule(config, item)
    ext = get_extension(item)
    route = rule.get("route", "archive")

    if route == "media":
        safe_move(
            item,
            expand_path(paths["media_incoming_dir"]),
            dry_run,
            check_duplicates=check_duplicates,
        )
        return

    if route == "media_assets":
        safe_move(
            item,
            expand_path(paths["media_assets_dir"]),
            dry_run,
            check_duplicates=check_duplicates,
        )
        return

    age = file_age_days(item)
    archive_after_days = rule.get("archive_after_days")

    if route == "review":
        if archive_after_days is not None and age >= archive_after_days:
            safe_move(
                item,
                expand_path(paths["to_review_dir"]),
                dry_run,
                check_duplicates=check_duplicates,
            )
        else:
            logging.info("NO ACTION %s ext=%s age_days=%.2f", item, ext, age)
        return

    if archive_after_days is not None and age >= archive_after_days:
        safe_move(
            item,
            expand_path(paths["auto_archive_dir"]),
            dry_run,
            check_duplicates=check_duplicates,
        )
    else:
        logging.info("NO ACTION %s ext=%s age_days=%.2f", item, ext, age)


def process_downloads_folder(
    source_dir: Path, config: dict, dry_run: bool, *, check_duplicates: bool
) -> int:
    errors = 0
    if not source_dir.exists():
        return errors

    for item in source_dir.iterdir():
        if not item.is_file():
            continue
        try:
            route_downloads_file(item, config, dry_run, check_duplicates=check_duplicates)
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
    *,
    check_duplicates: bool,
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
                    safe_move(
                        item,
                        target_dir,
                        dry_run,
                        check_duplicates=check_duplicates,
                    )
        except OSError as exc:
            logging.error("Failed to process %s: %s", item, exc)
            errors += 1

    return errors


def main() -> None:
    config = load_config()
    errors = validate_config(config)
    paths = config.get("paths", {})
    settings = config.get("settings", {})

    log_file_value = paths.get("log_file") if isinstance(paths, dict) else None
    log_file = expand_path(log_file_value) if log_file_value else BASE_DIR / "logs" / "download-manager.log"
    setup_logging(log_file)

    if errors:
        for error in errors:
            logging.error("Config validation: %s", error)
        sys.exit(1)

    dry_run = settings.get("dry_run", True)
    check_duplicates = settings.get("duplicate_detection", True)

    created_dirs = ensure_workspace(config)
    for directory in created_dirs:
        logging.info("Created directory: %s", directory)

    logging.info(
        "Download manager started. dry_run=%s duplicate_detection=%s bootstrap_created=%d",
        dry_run,
        check_duplicates,
        len(created_dirs),
    )

    downloads_dir = expand_path(paths["downloads_dir"])
    auto_archive_dir = expand_path(paths["auto_archive_dir"])
    trash_later_dir = expand_path(paths["trash_later_dir"])

    run_errors = 0
    run_errors += process_downloads_folder(
        downloads_dir, config, dry_run, check_duplicates=check_duplicates
    )
    run_errors += process_staged_folder(
        auto_archive_dir,
        trash_later_dir,
        "trash_after_days",
        config,
        dry_run,
        check_duplicates=check_duplicates,
    )
    run_errors += process_staged_folder(
        trash_later_dir,
        trash_later_dir,
        "delete_after_days",
        config,
        dry_run,
        check_duplicates=check_duplicates,
    )

    logging.info("Download manager finished. errors=%d", run_errors)

    if run_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
