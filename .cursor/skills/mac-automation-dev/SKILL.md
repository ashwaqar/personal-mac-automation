---
name: mac-automation-dev
description: Develop and extend the personal-mac-automation Downloads manager on macOS. Use when adding features, fixing bugs, writing tests, modifying download_manager.py, editing download-rules.yaml, or working on the 3-stage pipeline, config validation, duplicate detection, or workspace bootstrap.
---

# Mac Automation — Development

## Quick start

1. Read `AGENTS.md` and `configs/download-rules.yaml`
2. Activate venv: `source .venv/bin/activate`
3. Run tests: `.venv/bin/pytest tests/ -v`
4. Make focused changes; re-run tests

## Adding a new file type

Edit `configs/download-rules.yaml` only (no Python change needed):

```yaml
rules:
  csv:
    archive_after_days: 14
    trash_after_days: 45
    delete_after_days: 90
```

For immediate routing:

```yaml
  heic:
    route: media_assets
```

## Adding Python behavior

1. Change `scripts/download_manager.py`
2. Update `validate_config()` if config shape changes
3. Add tests in `tests/test_*.py`
4. Update `CHANGELOG.md` for user-facing changes

## Test isolation

```python
config, config_path, dirs = make_config(tmp_path, dry_run=False)
dm = reload_download_manager(monkeypatch, config_path)
set_file_age_days(file, days)
dm.main()
```

Env var: `DOWNLOAD_RULES_CONFIG` points to temp config.

## Pipeline invariants (do not break)

- Stage 1 only: media, media_assets, review, archive routing
- Stage 2 only: `trash_after_days` in AutoArchive
- Stage 3 only: `delete_after_days` in TrashLater
- `dry_run=true` must not modify files
- `bootstrap_folders` creates dirs even in dry_run

## Reference

See [reference.md](reference.md) for function map and folder hierarchy.
