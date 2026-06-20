# Architecture

## Objective

Personal Mac automation platform designed to automate file organization, cleanup, and future AI-assisted workflows while maintaining complete user isolation.

## Design Principles

* User-scoped execution only
* Configuration-driven behavior
* Safe multi-stage file lifecycle
* Git-managed automation platform
* Future AI extensibility
* Minimal system-wide dependencies

## Core Components

### 1. Rules Engine

Configuration is defined in:

```text
configs/download-rules.yaml
```

The rules engine determines:

* File retention periods
* Routing behavior
* Archive policies
* Deletion policies
* Review policies

### 2. Automation Engine

Implemented in:

```text
scripts/download_manager.py
```

Responsibilities:

* Stage 1: Scan `~/Downloads` and route or archive files
* Stage 2: Progress `~/Downloads/AutoArchive` to TrashLater
* Stage 3: Delete aged files from `~/Downloads/TrashLater`
* Generate logs

Each age threshold applies only in its stage folder. Media and review routing happen exclusively in stage 1.

### 3. Logging Layer

Logs are stored in:

```text
logs/download-manager.log
```

The logging layer provides:

* Traceability
* Troubleshooting
* Auditability

### 4. Scheduling Layer

Implemented using:

```text
launchd
```

The repository includes `launchd/com.ashwaq.downloadmanager.plist`, scheduled for **every Monday at 7:00 AM**.

Execution is performed through a user-level LaunchAgent:

```text
~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist
```

This ensures:

* No system-wide installation
* User-specific execution
* Automatic scheduling

### 5. Future AI Layer

Planned integrations:

* Hermes Agent
* Ollama
* Local file classification
* Obsidian automation
* Work summary generation

## File Lifecycle

```text
Stage 1 — ~/Downloads
    ├─ media / media_assets → routed immediately
    ├─ unknown types (review) → ToReview when aged (default: 14 days)
    └─ standard types → AutoArchive when aged

Stage 2 — ~/Downloads/AutoArchive → TrashLater when aged

Stage 3 — ~/Downloads/TrashLater → permanent delete when aged
```

### Downloads

Active working area. Only this folder receives immediate media routing and age-gated review/archive decisions.

### AutoArchive

Temporary retention area. Files progress to TrashLater when they exceed `trash_after_days` for their extension.

### TrashLater

Final retention stage before deletion. Files are permanently removed when they exceed `delete_after_days`.

### Delete

Permanent removal after configured retention periods (`path.unlink()`).

## Media Workflow

```text
Downloads
    ↓ (immediate)
Media/Videos/Incoming     (video: mp4, mov, mkv)
Media/Assets/Downloads    (audio: mp3, wav)
```

## Review Workflow

Unknown file types use the default rule (`route: review`). They remain in Downloads until `archive_after_days` is reached, then move to:

```text
Downloads/ToReview
```

for manual inspection.

## Security Model

### User Isolation

The automation uses:

```python
Path.home()
```

and therefore only operates within the currently logged-in user's home directory.

### Multi-User Safety

The automation does not access:

* Other user home directories
* System folders
* Shared user data

## Future Roadmap

* AI-assisted classification
* Intelligent document routing
* Obsidian integration
* Weekly work summaries
* Personal AI Operating System
