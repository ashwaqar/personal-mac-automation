from __future__ import annotations

import importlib
import sys

import pytest
import yaml

from conftest import REPO_ROOT, make_config, reload_download_manager

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import download_manager


def test_validate_config_accepts_valid_config(workspace):
    errors = download_manager.validate_config(workspace["config"])
    assert errors == []


def test_validate_config_rejects_missing_paths(tmp_path):
    config = {"settings": {"dry_run": True}, "paths": {}, "rules": {}}
    errors = download_manager.validate_config(config)
    assert any("paths.downloads_dir is required" in error for error in errors)


def test_validate_config_rejects_invalid_route(tmp_path):
    config, _, _ = make_config(tmp_path)
    config["rules"]["txt"] = {"route": "invalid"}
    errors = download_manager.validate_config(config)
    assert any("rules.txt.route must be one of" in error for error in errors)


def test_validate_config_rejects_threshold_order(tmp_path):
    config, _, _ = make_config(tmp_path)
    config["rules"]["txt"] = {
        "archive_after_days": 30,
        "trash_after_days": 10,
        "delete_after_days": 60,
    }
    errors = download_manager.validate_config(config)
    assert any("ascending order" in error for error in errors)


def test_validate_config_requires_review_archive_days(tmp_path):
    config, _, _ = make_config(tmp_path)
    config["default"] = {"route": "review"}
    errors = download_manager.validate_config(config)
    assert any("route: review requires archive_after_days" in error for error in errors)


def test_main_exits_on_invalid_config(tmp_path, monkeypatch):
    config_path = tmp_path / "download-rules.yaml"
    config_path.write_text(
        yaml.dump({"settings": {"dry_run": True}, "paths": {}}),
        encoding="utf-8",
    )
    dm = reload_download_manager(monkeypatch, config_path)

    with pytest.raises(SystemExit) as exc:
        dm.main()

    assert exc.value.code == 1
