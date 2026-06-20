# Changelog

## v0.2.0

### Added

- YAML config validation on startup (required paths, valid routes, threshold ordering)
- Duplicate file detection via SHA-256 content hash (removes re-downloaded duplicates)
- `settings.duplicate_detection` config flag (default: `true`)
- Tests for config validation and duplicate detection

### Changed

- Production mode enabled (`dry_run: false`)
- LaunchAgent installed locally with Monday 7 AM schedule from repo plist

---

## v0.1.1

### Fixed

- Restored full 3-stage Downloads pipeline (Downloads → AutoArchive → TrashLater → Delete)
- Age thresholds now apply per stage folder instead of all at once on Downloads
- Age-gated review routing for unknown file types (default: 14 days before ToReview)

### Added

- `route_downloads_file()` and `process_staged_folder()` split in `download_manager.py`
- Collision-safe moves (`_1`, `_2` suffix on duplicate filenames)
- Per-file error handling with non-zero exit code on failures
- `DOWNLOAD_RULES_CONFIG` environment variable for test isolation
- pytest test suite (`tests/test_download_manager.py`, 8 test cases)
- LaunchAgent plist in repo (`launchd/com.ashwaq.downloadmanager.plist`, Monday 7 AM)
- `*.bak` in `.gitignore`

### Changed

- `dry_run: true` is now the default in `configs/download-rules.yaml`
- Removed unused `media_to_sort_dir` config key
- Documentation updated to match implemented behavior

---

## v0.1.0

### Added

- Downloads automation
- YAML configuration
- Logging
- LaunchAgent integration
- Media routing
- ToReview queue
- GitHub repository

### Planned

- AI classification
- Obsidian integration
- Hermes Agent
- Backup automation
