from __future__ import annotations

import importlib
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def make_config(
    tmp_path: Path,
    *,
    dry_run: bool = False,
) -> tuple[dict, Path, dict[str, Path]]:
    downloads = tmp_path / "Downloads"
    auto_archive = downloads / "AutoArchive"
    trash_later = downloads / "TrashLater"
    to_review = downloads / "ToReview"
    media_incoming = tmp_path / "Media" / "Videos" / "Incoming"
    media_assets = tmp_path / "Media" / "Assets" / "Downloads"
    log_file = tmp_path / "logs" / "download-manager.log"

    for directory in (
        downloads,
        auto_archive,
        trash_later,
        to_review,
        media_incoming,
        media_assets,
        log_file.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    config = {
        "settings": {"dry_run": dry_run},
        "paths": {
            "downloads_dir": str(downloads),
            "auto_archive_dir": str(auto_archive),
            "trash_later_dir": str(trash_later),
            "to_review_dir": str(to_review),
            "media_incoming_dir": str(media_incoming),
            "media_assets_dir": str(media_assets),
            "log_file": str(log_file),
        },
        "rules": {
            "dmg": {
                "archive_after_days": 3,
                "trash_after_days": 14,
                "delete_after_days": 30,
            },
            "pkg": {
                "archive_after_days": 3,
                "trash_after_days": 14,
                "delete_after_days": 30,
            },
            "zip": {
                "archive_after_days": 7,
                "trash_after_days": 30,
                "delete_after_days": 60,
            },
            "pdf": {
                "archive_after_days": 30,
                "trash_after_days": 90,
                "delete_after_days": 120,
            },
            "docx": {
                "archive_after_days": 30,
                "trash_after_days": 90,
                "delete_after_days": 120,
            },
            "xlsx": {
                "archive_after_days": 30,
                "trash_after_days": 90,
                "delete_after_days": 120,
            },
            "mp4": {"route": "media"},
            "mov": {"route": "media"},
            "mkv": {"route": "media"},
            "mp3": {"route": "media_assets"},
            "wav": {"route": "media_assets"},
        },
        "default": {"route": "review", "archive_after_days": 14},
    }

    config_path = tmp_path / "download-rules.yaml"
    config_path.write_text(yaml.dump(config), encoding="utf-8")

    dirs = {
        "downloads": downloads,
        "auto_archive": auto_archive,
        "trash_later": trash_later,
        "to_review": to_review,
        "media_incoming": media_incoming,
        "media_assets": media_assets,
        "log_file": log_file,
    }
    return config, config_path, dirs


def set_file_age_days(path: Path, days: float) -> None:
    mtime = (datetime.now() - timedelta(days=days)).timestamp()
    os.utime(path, (mtime, mtime))


def reload_download_manager(monkeypatch: pytest.MonkeyPatch, config_path: Path):
    monkeypatch.setenv("DOWNLOAD_RULES_CONFIG", str(config_path))
    import download_manager

    return importlib.reload(download_manager)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    config, config_path, dirs = make_config(tmp_path, dry_run=False)
    dm = reload_download_manager(monkeypatch, config_path)
    return {
        "config": config,
        "config_path": config_path,
        "dirs": dirs,
        "dm": dm,
        "tmp_path": tmp_path,
        "monkeypatch": monkeypatch,
    }


@pytest.fixture
def dry_run_workspace(tmp_path, monkeypatch):
    config, config_path, dirs = make_config(tmp_path, dry_run=True)
    dm = reload_download_manager(monkeypatch, config_path)
    return {
        "config": config,
        "config_path": config_path,
        "dirs": dirs,
        "dm": dm,
        "tmp_path": tmp_path,
        "monkeypatch": monkeypatch,
    }
