from __future__ import annotations

from conftest import make_config, reload_download_manager, set_file_age_days


def test_media_routing(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_incoming = workspace["dirs"]["media_incoming"]
    dm = workspace["dm"]

    video = downloads / "clip.mp4"
    video.write_text("video", encoding="utf-8")

    dm.main()

    assert not video.exists()
    assert (media_incoming / "clip.mp4").exists()


def test_media_assets_routing(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_assets = workspace["dirs"]["media_assets"]
    dm = workspace["dm"]

    audio = downloads / "song.mp3"
    audio.write_text("audio", encoding="utf-8")

    dm.main()

    assert not audio.exists()
    assert (media_assets / "song.mp3").exists()


def test_review_age_gated(workspace):
    downloads = workspace["dirs"]["downloads"]
    to_review = workspace["dirs"]["to_review"]
    dm = workspace["dm"]

    young = downloads / "unknown.xyz"
    young.write_text("young", encoding="utf-8")
    set_file_age_days(young, 5)

    aged = downloads / "old.xyz"
    aged.write_text("aged", encoding="utf-8")
    set_file_age_days(aged, 15)

    dm.main()

    assert young.exists()
    assert not (to_review / "unknown.xyz").exists()
    assert not aged.exists()
    assert (to_review / "old.xyz").exists()


def test_archive_stage(workspace):
    downloads = workspace["dirs"]["downloads"]
    auto_archive = workspace["dirs"]["auto_archive"]
    dm = workspace["dm"]

    pdf = downloads / "report.pdf"
    pdf.write_text("pdf", encoding="utf-8")
    set_file_age_days(pdf, 31)

    dm.main()

    assert not pdf.exists()
    assert (auto_archive / "report.pdf").exists()


def test_trash_stage(workspace):
    auto_archive = workspace["dirs"]["auto_archive"]
    trash_later = workspace["dirs"]["trash_later"]
    dm = workspace["dm"]

    staged = auto_archive / "installer.dmg"
    staged.write_text("dmg", encoding="utf-8")
    set_file_age_days(staged, 15)

    dm.main()

    assert not staged.exists()
    assert (trash_later / "installer.dmg").exists()


def test_delete_stage(workspace):
    trash_later = workspace["dirs"]["trash_later"]
    dm = workspace["dm"]

    doomed = trash_later / "old.pkg"
    doomed.write_text("pkg", encoding="utf-8")
    set_file_age_days(doomed, 31)

    dm.main()

    assert not doomed.exists()


def test_dry_run_no_changes(dry_run_workspace):
    downloads = dry_run_workspace["dirs"]["downloads"]
    media_incoming = dry_run_workspace["dirs"]["media_incoming"]
    dm = dry_run_workspace["dm"]

    video = downloads / "clip.mp4"
    video.write_text("video", encoding="utf-8")

    dm.main()

    assert video.exists()
    assert not (media_incoming / "clip.mp4").exists()


def test_collision_handling(workspace):
    downloads = workspace["dirs"]["downloads"]
    media_incoming = workspace["dirs"]["media_incoming"]
    dm = workspace["dm"]

    existing = media_incoming / "clip.mp4"
    existing.write_text("existing", encoding="utf-8")

    incoming = downloads / "clip.mp4"
    incoming.write_text("incoming", encoding="utf-8")

    dm.main()

    assert not incoming.exists()
    assert existing.exists()
    assert (media_incoming / "clip_1.mp4").exists()


def test_three_stage_full_lifecycle(workspace):
    downloads = workspace["dirs"]["downloads"]
    auto_archive = workspace["dirs"]["auto_archive"]
    trash_later = workspace["dirs"]["trash_later"]
    dm = workspace["dm"]

    pdf = downloads / "lifecycle.pdf"
    pdf.write_text("pdf", encoding="utf-8")
    set_file_age_days(pdf, 31)

    dm.main()
    archived = auto_archive / "lifecycle.pdf"
    assert archived.exists()

    set_file_age_days(archived, 91)
    dm.main()
    trashed = trash_later / "lifecycle.pdf"
    assert trashed.exists()

    set_file_age_days(trashed, 121)
    dm.main()
    assert not trashed.exists()
