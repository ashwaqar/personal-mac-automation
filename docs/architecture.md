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

* Scan Downloads directory
* Evaluate file age
* Apply routing rules
* Execute file moves
* Generate logs

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

Execution is performed through a user-level LaunchAgent.

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
Downloads
    ↓
AutoArchive
    ↓
TrashLater
    ↓
Delete
```

### Downloads

Active working area.

### AutoArchive

Temporary retention area for files that are no longer actively used.

### TrashLater

Final retention stage before deletion.

### Delete

Permanent removal after configured retention periods.

## Media Workflow

```text
Downloads
    ↓
Media Routing
    ↓
Media/Videos/Incoming
```

Supported media types:

* mp4
* mov
* mkv

## Review Workflow

Unknown file types are routed to:

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
