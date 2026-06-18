# personal-mac-automation

Personal macOS automation platform focused on file organization, system maintenance, productivity workflows, and future local AI integration.

---

# Overview

This project was created to build a maintainable, Git-backed automation platform for a personal MacBook.

The primary goals are:

* Keep the Downloads folder clean automatically
* Reduce manual file management
* Maintain a structured folder hierarchy
* Support future AI-assisted workflows
* Preserve user isolation on multi-user Macs
* Build a foundation for a personal AI operating system

The platform is designed specifically for:

* macOS
* Python-based automation
* LaunchAgent scheduling
* Local-first operation
* Future AI agent integration

---

# Features

## Downloads Automation

Automatically manages downloaded files using configurable rules.

Workflow:

```text
Downloads
    ↓
AutoArchive
    ↓
TrashLater
    ↓
Delete
```

Benefits:

* Prevents Downloads folder clutter
* Provides multiple recovery stages
* Reduces accidental deletion
* Enables long-term automation

---

## Media Routing

Automatically routes media files to dedicated media folders.

Supported:

* mp4
* mov
* mkv
* mp3
* wav

Workflow:

```text
Downloads
    ↓
Media Routing
    ↓
Media/Videos/Incoming
```

---

## Review Queue

Unknown file types are moved into:

```text
Downloads/ToReview
```

This allows manual review before any action is taken.

---

## Logging

All operations are logged.

Log file:

```text
logs/download-manager.log
```

Provides:

* Traceability
* Troubleshooting
* Auditability

---

## User Isolation

The automation operates only within the current user's home directory.

Implementation:

```python
Path.home()
```

Benefits:

* Safe for shared Macs
* Does not affect other users
* No system-wide access required

---

# Architecture

## Core Components

### Rules Engine

Configuration-driven behavior.

Location:

```text
configs/download-rules.yaml
```

Controls:

* Retention periods
* Routing behavior
* Cleanup policies
* Dry-run mode

---

### Automation Engine

Location:

```text
scripts/download_manager.py
```

Responsibilities:

* Scan Downloads
* Evaluate file age
* Apply routing rules
* Move files
* Delete files
* Generate logs

---

### Logging Layer

Location:

```text
logs/download-manager.log
```

Captures:

* Moves
* Deletes
* Routing decisions
* Errors

---

### Scheduling Layer

Implemented using:

```text
launchd
```

Execution:

```text
~/Library/LaunchAgents
```

Benefits:

* User-specific execution
* Automatic scheduling
* Native macOS integration

---

### Future AI Layer

Planned integrations:

* Hermes Agent
* Ollama
* Local LLMs
* Obsidian automation
* Weekly work summaries
* Personal knowledge management

---

# Folder Structure

## Projects

```text
~/Projects
├── Active
├── Learning
├── Ideas
├── Experiments
├── Completed
└── personal-mac-automation
```

---

## Notes

```text
~/Notes
└── ObsidianVault
```

---

## Media

```text
~/Media
├── Videos
│   ├── Incoming
│   ├── ToSort
│   ├── Raw
│   └── Final
├── Photos
├── ScreenRecordings
├── Audio
└── Exports
```

---

## Documents

```text
~/Documents
├── Finance
├── Insurance
├── Travel
├── Certificates
├── Purchases
└── Family
```

---

## Archive

```text
~/Archive
├── Projects
├── Documents
├── Media
└── Downloads
```

---

# Prerequisites

Required:

* macOS
* Homebrew
* Git
* Python 3

Recommended:

* iTerm2
* Oh My Zsh
* Powerlevel10k
* Obsidian

---

# Initial Setup

## Create Project Structure

```bash
mkdir -p ~/Projects/personal-mac-automation

cd ~/Projects/personal-mac-automation

mkdir -p \
scripts \
configs \
launchd \
docs \
logs \
tests \
ai
```

---

## Create Downloads Workflow Folders

```bash
mkdir -p ~/Downloads/AutoArchive
mkdir -p ~/Downloads/TrashLater
mkdir -p ~/Downloads/ToReview

mkdir -p ~/Media/Videos/Incoming
mkdir -p ~/Media/Videos/ToSort

mkdir -p ~/Media/Assets/Downloads
```

---

## Create Python Virtual Environment

```bash
cd ~/Projects/personal-mac-automation

python3 -m venv .venv

source .venv/bin/activate

pip install pyyaml

pip freeze > requirements.txt
```

---

# Running the Automation

Activate environment:

```bash
source .venv/bin/activate
```

Run manually:

```bash
python scripts/download_manager.py
```

---

# LaunchAgent Scheduling

Create:

```text
~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist
```

Benefits:

* Runs automatically
* User-specific execution
* No system-wide services

---

# Git Workflow

Initialize:

```bash
git init
```

Commit:

```bash
git add .
git commit -m "Initial commit"
```

Connect repository:

```bash
git remote add origin git@github.com:ashwaqar/personal-mac-automation.git
```

Push:

```bash
git branch -M main
git push -u origin main
```

---

# SSH Setup

Generate key:

```bash
ssh-keygen -t ed25519 -C "ashwaqar@gmail.com"
```

Add to keychain:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

Test:

```bash
ssh -T git@github.com
```

Expected:

```text
Hi ashwaqar! You've successfully authenticated...
```

---

# Multi-User Mac Strategy

This Mac is configured with:

* User 1: Ashwaq
* User 2: Wife

Both users have:

* Separate home directories
* Separate Apple IDs
* Separate iCloud accounts
* Separate browser profiles
* Separate Downloads folders

The automation only runs for Ashwaq's account.

---

# Troubleshooting

## Files Are Not Moving

Check:

```yaml
settings:
  dry_run: false
```

Verify:

```bash
cat logs/download-manager.log
```

---

## Zsh Errors

Verify:

```text
~/.oh-my-zsh/oh-my-zsh.sh
```

exists.

---

## LaunchAgent Not Running

Check:

```bash
launchctl list | grep downloadmanager
```

---

# Roadmap

## v0.1

Completed

* Downloads automation
* YAML configuration
* Logging
* LaunchAgent scheduling
* Media routing
* Review routing
* User isolation

---

## v0.2

Planned

* Duplicate detection
* Configuration validation
* Archive reporting
* Retention analytics

---

## v0.3

Planned

* Obsidian integration
* Daily note automation
* Weekly reports
* Monthly summaries

---

## v0.4

Planned

* Local AI integration
* File classification
* Knowledge extraction
* Productivity workflows

---

## v0.5

Planned

* Hermes Agent integration
* Agent-based file management
* Agent-based note management
* Automation orchestration

---

## v1.0

Personal AI Operating System

Capabilities:

* Autonomous file organization
* Knowledge management
* Work tracking
* Weekly reporting
* Local AI assistance
* Agent-driven workflows

---

# License

MIT License

See the LICENSE file for details.
