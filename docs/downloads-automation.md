# Downloads Automation

## Overview

The Downloads Automation system automatically organizes downloaded files using configurable retention and routing policies.

## Objectives

* Keep Downloads folder clean
* Reduce manual file management
* Preserve important files
* Enable future AI-assisted organization

## Workflow

```text
Downloads
    ↓
AutoArchive
    ↓
TrashLater
    ↓
Delete
```

## Folder Definitions

### Downloads

Primary landing zone for all downloaded files.

### AutoArchive

Intermediate retention area.

Files remain available for recovery before moving to the next stage.

### TrashLater

Final retention area before permanent deletion.

### ToReview

Manual review area for unknown file types.

## Configuration

Rules are defined in:

```text
configs/download-rules.yaml
```

Configuration controls:

* Archive thresholds
* Trash thresholds
* Delete thresholds
* Routing destinations
* Dry-run behavior

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

## Logging

All operations are logged to:

```text
logs/download-manager.log
```

## Safety Features

### Dry Run Mode

Allows validation without moving files.

### User Isolation

Operates only within the current user's home directory.

### Multi-Stage Retention

Prevents accidental deletion through staged cleanup.
