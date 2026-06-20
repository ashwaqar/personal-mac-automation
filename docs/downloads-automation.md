# Downloads Automation

## Overview

The Downloads Automation system automatically organizes downloaded files using configurable retention and routing policies.

## Objectives

* Keep Downloads folder clean
* Reduce manual file management
* Preserve important files
* Enable future AI-assisted organization

## Workflow

The pipeline runs in three sequential stages. Each age threshold applies only in its stage folder.

```text
Stage 1 — ~/Downloads
    ├─ media / media_assets → routed immediately
    ├─ unknown types (review) → ToReview when aged
    └─ standard types → AutoArchive when aged

Stage 2 — ~/Downloads/AutoArchive → TrashLater when aged

Stage 3 — ~/Downloads/TrashLater → permanent delete when aged
```

## Folder Definitions

### Downloads

Primary landing zone for all downloaded files. Stage 1 scans only the top level (not subdirectories).

### AutoArchive

Intermediate retention area. Stage 2 moves files to TrashLater when they exceed `trash_after_days`.

### TrashLater

Final retention area before permanent deletion. Stage 3 deletes files when they exceed `delete_after_days`.

### ToReview

Manual review area for unknown file types. Files move here from Downloads only after reaching `archive_after_days` under the default `route: review` rule.

## Configuration

Rules are defined in:

```text
configs/download-rules.yaml
```

Configuration controls:

* Archive thresholds (stage 1, Downloads only)
* Trash thresholds (stage 2, AutoArchive only)
* Delete thresholds (stage 3, TrashLater only)
* Routing destinations
* Dry-run behavior

**Default:** `dry_run: true` — safe mode until production is enabled.

## Supported Document Types

* pdf
* docx
* xlsx

## Supported Installer Types

* dmg
* pkg
* zip

## Supported Media Types

* mp4
* mov
* mkv
* mp3
* wav

## Logging

All operations are logged to:

```text
logs/download-manager.log
```

## Safety Features

### Dry Run Mode

Allows validation without moving files. Enabled by default.

### User Isolation

Operates only within the current user's home directory.

### Multi-Stage Retention

Prevents accidental deletion through staged cleanup.

### Collision-Safe Moves

If a destination file already exists, the mover appends `_1`, `_2`, etc. before the extension instead of overwriting.

## Scheduling

LaunchAgent plist: `launchd/com.ashwaq.downloadmanager.plist`

Runs every **Monday at 7:00 AM** when loaded into `~/Library/LaunchAgents/`.

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
```

Tests use isolated temp directories via the `DOWNLOAD_RULES_CONFIG` environment variable.
