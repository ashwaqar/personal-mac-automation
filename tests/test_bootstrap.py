from __future__ import annotations

import yaml

from conftest import make_config, reload_download_manager


def _fresh_config(tmp_path, **settings_overrides):
    root = tmp_path / "home"
    config = {
        "settings": {
            "dry_run": True,
            "bootstrap_folders": True,
            **settings_overrides,
        },
        "paths": {
            "downloads_dir": str(root / "Downloads"),
            "auto_archive_dir": str(root / "Downloads" / "AutoArchive"),
            "trash_later_dir": str(root / "Downloads" / "TrashLater"),
            "to_review_dir": str(root / "Downloads" / "ToReview"),
            "media_incoming_dir": str(root / "Media" / "Videos" / "Incoming"),
            "media_assets_dir": str(root / "Media" / "Assets" / "Downloads"),
            "log_file": str(root / "Projects" / "personal-mac-automation" / "logs" / "download-manager.log"),
        },
        "bootstrap_dirs": [
            str(root / "Projects" / "Active"),
            str(root / "Documents" / "Finance"),
        ],
        "rules": {},
        "default": {"route": "review", "archive_after_days": 14},
    }
    config_path = tmp_path / "download-rules.yaml"
    config_path.write_text(yaml.dump(config), encoding="utf-8")
    return config, config_path, root


def test_ensure_workspace_creates_automation_paths(tmp_path, monkeypatch):
    config, config_path, root = _fresh_config(tmp_path)
    dm = reload_download_manager(monkeypatch, config_path)

    created = dm.ensure_workspace(config)

    assert (root / "Downloads" / "AutoArchive").is_dir()
    assert (root / "Media" / "Videos" / "Incoming").is_dir()
    assert (root / "Projects" / "personal-mac-automation" / "logs").is_dir()
    assert len(created) >= 7


def test_ensure_workspace_creates_bootstrap_dirs(tmp_path, monkeypatch):
    config, config_path, root = _fresh_config(tmp_path)
    dm = reload_download_manager(monkeypatch, config_path)

    created = dm.ensure_workspace(config)

    assert (root / "Projects" / "Active").is_dir()
    assert (root / "Documents" / "Finance").is_dir()
    assert any(path.name == "Active" for path in created)


def test_bootstrap_folders_disabled(tmp_path, monkeypatch):
    config, config_path, root = _fresh_config(tmp_path, bootstrap_folders=False)
    dm = reload_download_manager(monkeypatch, config_path)

    created = dm.ensure_workspace(config)

    assert created == []
    assert not (root / "Downloads" / "AutoArchive").exists()


def test_ensure_workspace_is_idempotent(tmp_path, monkeypatch):
    config, config_path, _ = _fresh_config(tmp_path)
    dm = reload_download_manager(monkeypatch, config_path)

    first = dm.ensure_workspace(config)
    second = dm.ensure_workspace(config)

    assert len(first) > 0
    assert second == []


def test_main_bootstraps_before_processing(tmp_path, monkeypatch):
    config, config_path, root = _fresh_config(tmp_path)
    dm = reload_download_manager(monkeypatch, config_path)

    dm.main()

    assert (root / "Downloads" / "AutoArchive").is_dir()
    assert (root / "Projects" / "Active").is_dir()


def test_validate_config_rejects_invalid_bootstrap_dirs(tmp_path):
    from conftest import REPO_ROOT
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import download_manager

    config, _, _ = make_config(tmp_path)
    config["bootstrap_dirs"] = ["valid", 123]
    errors = download_manager.validate_config(config)
    assert any("bootstrap_dirs[1]" in error for error in errors)
