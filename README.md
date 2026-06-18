# personal-mac-automation

Automation toolkit for a MacBook setup focused on Downloads cleanup, folder structure, and future local AI integration.

## Purpose

This repository is designed for a single macOS user account on a personal MacBook. It keeps the automation configuration, scripts, launchd jobs, and documentation in one Git-backed place.

## What this repository contains

- `configs/` — YAML configuration for cleanup rules
- `scripts/` — Python automation scripts
- `launchd/` — macOS LaunchAgent examples
- `docs/` — setup notes and operational guidance
- `logs/` — runtime logs
- `tests/` — test fixtures and validation notes
- `ai/` — future local AI integration notes

## Target audience

This repository is intended to run only for the current macOS user account. The scripts use the current user's home directory and are designed to avoid affecting other user accounts on the same machine.

## Current workflow

```text
Downloads
  ├── AutoArchive
  ├── TrashLater
  └── ToReview

Media
  ├── Videos
  │   ├── Incoming
  │   └── ToSort
  └── Assets
      └── Downloads
```

## Prerequisites

- macOS
- Homebrew
- Python 3
- Git
- iTerm2 (recommended)
- Oh My Zsh + Powerlevel10k (recommended)

## One-time setup

### 1. Create the project folders

```bash
mkdir -p ~/Projects/personal-mac-automation
cd ~/Projects/personal-mac-automation
mkdir -p scripts configs launchd docs logs tests ai
```

### 2. Create the downloads staging folders

```bash
mkdir -p ~/Downloads/AutoArchive
mkdir -p ~/Downloads/TrashLater
mkdir -p ~/Downloads/ToReview
mkdir -p ~/Media/Videos/Incoming
mkdir -p ~/Media/Videos/ToSort
mkdir -p ~/Media/Assets/Downloads
```

### 3. Create the Python virtual environment

```bash
cd ~/Projects/personal-mac-automation
python3 -m venv .venv
source .venv/bin/activate
pip install pyyaml
pip freeze > requirements.txt
```

### 4. Add the configuration file

Create `configs/download-rules.yaml` and use it to control:

- retention days
- dry-run mode
- destination paths
- routing rules for file extensions

### 5. Run the script manually

```bash
cd ~/Projects/personal-mac-automation
source .venv/bin/activate
python scripts/download_manager.py
```

### 6. Schedule it with LaunchAgent

Use a user-level LaunchAgent in `~/Library/LaunchAgents` so the job runs only for this macOS user account.

## Recommended folder structure

### Projects

```text
~/Projects
├── Active
├── Learning
├── Ideas
├── Experiments
├── Completed
└── personal-mac-automation
```

### Notes

```text
~/Notes
└── ObsidianVault
```

### Media

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

### Documents

```text
~/Documents
├── Finance
├── Insurance
├── Travel
├── Certificates
├── Purchases
└── Family
```

### Archive

```text
~/Archive
├── Projects
├── Documents
├── Media
└── Downloads
```

## Git workflow

When you are ready to initialize Git:

```bash
cd ~/Projects/personal-mac-automation
git init
git add .
git commit -m "Initial commit"
```

Then create a new repository on GitHub and add the remote:

```bash
git remote add origin git@github.com:<your-user>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Troubleshooting

### `source ~/.zshrc` fails

If Oh My Zsh is not installed correctly, reinstall it and confirm that this file exists:

```text
~/.oh-my-zsh/oh-my-zsh.sh
```

### Files are not moving

Check:

- `settings.dry_run`
- the file age values in `configs/download-rules.yaml`
- the log file at `~/Projects/personal-mac-automation/logs/download-manager.log`

### Nothing happens for my wife’s account

That is expected. The automation is intended to run only under the current user account because it uses `Path.home()` and a user-level LaunchAgent.

## Future ideas

- AI-assisted classification for unknown files
- smarter routing for invoices, videos, and course downloads
- backup automation
- Obsidian maintenance scripts
- dotfile management
