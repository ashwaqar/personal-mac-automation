from __future__ import annotations

from conftest import set_file_age_days


def test_duplicate_content_removed_instead_of_moved(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_incoming = workspace["dirs"]["media_incoming"]
    dm = workspace["dm"]

    existing = media_incoming / "clip.mp4"
    existing.write_bytes(b"same-content")

    duplicate = downloads / "clip.mp4"
    duplicate.write_bytes(b"same-content")

    dm.main()

    assert not duplicate.exists()
    assert existing.exists()
    assert not (media_incoming / "clip_1.mp4").exists()


def test_different_content_uses_collision_suffix(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_incoming = workspace["dirs"]["media_incoming"]
    dm = workspace["dm"]

    existing = media_incoming / "clip.mp4"
    existing.write_bytes(b"original")

    incoming = downloads / "clip.mp4"
    incoming.write_bytes(b"different")

    dm.main()

    assert not incoming.exists()
    assert existing.exists()
    assert (media_incoming / "clip_1.mp4").exists()


def test_duplicate_detection_can_be_disabled(tmp_path, monkeypatch):
    from conftest import make_config, reload_download_manager

    config, config_path, dirs = make_config(tmp_path, dry_run=False)
    config["settings"]["duplicate_detection"] = False
    config_path.write_text(__import__("yaml").dump(config), encoding="utf-8")
    dm = reload_download_manager(monkeypatch, config_path)

    existing = dirs["media_incoming"] / "clip.mp4"
    existing.write_bytes(b"same-content")

    duplicate = dirs["downloads"] / "clip.mp4"
    duplicate.write_bytes(b"same-content")

    dm.main()

    assert not duplicate.exists()
    assert existing.exists()
    assert (dirs["media_incoming"] / "clip_1.mp4").exists()


def test_duplicate_requires_same_filename(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_incoming = workspace["dirs"]["media_incoming"]
    dm = workspace["dm"]

    existing = media_incoming / "other.mp4"
    existing.write_bytes(b"shared-content")

    incoming = downloads / "clip.mp4"
    incoming.write_bytes(b"shared-content")

    dm.main()

    assert not incoming.exists()
    assert existing.exists()
    assert (media_incoming / "clip.mp4").exists()


def test_dry_run_duplicate_not_removed(dry_run_workspace):
    downloads = dry_run_workspace["dirs"]["downloads"]
    media_incoming = dry_run_workspace["dirs"]["media_incoming"]
    dm = dry_run_workspace["dm"]

    existing = media_incoming / "clip.mp4"
    existing.write_bytes(b"same-content")

    duplicate = downloads / "clip.mp4"
    duplicate.write_bytes(b"same-content")

    dm.main()

    assert duplicate.exists()
    assert existing.exists()


def test_size_mismatch_skips_duplicate_removal(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_incoming = workspace["dirs"]["media_incoming"]
    dm = workspace["dm"]

    existing = media_incoming / "clip.mp4"
    existing.write_bytes(b"short")

    incoming = downloads / "clip.mp4"
    incoming.write_bytes(b"much-longer-content")

    dm.main()

    assert not incoming.exists()
    assert existing.exists()
    assert (media_incoming / "clip_1.mp4").exists()


def test_duplicate_detection_on_archive_stage(workspace):
    downloads = workspace["dirs"]["downloads"]
    auto_archive = workspace["dirs"]["auto_archive"]
    dm = workspace["dm"]

    existing = auto_archive / "report.pdf"
    existing.write_bytes(b"same-pdf")
    set_file_age_days(existing, 40)

    duplicate = downloads / "report.pdf"
    duplicate.write_bytes(b"same-pdf")
    set_file_age_days(duplicate, 31)

    dm.main()

    assert not duplicate.exists()
    assert existing.exists()
    assert not (auto_archive / "report_1.pdf").exists()
