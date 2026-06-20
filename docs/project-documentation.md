# personal-mac-automation — Project Documentation

> Comprehensive reference for the personal macOS automation platform (v0.1.1).
> Last updated: 2026-06-20

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Vision and Goals](#vision-and-goals)
3. [Repository Structure](#repository-structure)
4. [System Architecture](#system-architecture)
5. [Downloads Automation Engine](#downloads-automation-engine)
6. [Configuration Reference](#configuration-reference)
7. [File Lifecycle and Routing](#file-lifecycle-and-routing)
8. [Personal Folder Hierarchy](#personal-folder-hierarchy)
9. [Runtime and Scheduling](#runtime-and-scheduling)
10. [Logging and Observability](#logging-and-observability)
11. [Security and Multi-User Model](#security-and-multi-user-model)
12. [Development Setup](#development-setup)
13. [Known Limitations and Gaps](#known-limitations-and-gaps)
14. [Roadmap](#roadmap)
15. [Git History](#git-history)

---

## Executive Summary

**personal-mac-automation** is a Git-backed, Python-based automation platform for a personal MacBook. Its first shipped capability is a **Downloads folder manager** that organizes files by extension using YAML rules — routing media to dedicated folders, sending unknown types to a review queue (age-gated), and aging other files through staged retention folders.

The project is intentionally scoped to:

- Run **only inside the current user's home directory** (`Path.home()`)
- Be **configuration-driven** (no code changes needed for new file types)
- Integrate with **macOS launchd** for scheduled execution
- Serve as a **foundation** for future local AI, Obsidian, and agent-based workflows

**Current state:** v0.1.1 — Full 3-stage pipeline is implemented with media/review routing in stage 1, pytest coverage, and a version-controlled LaunchAgent plist.

---

## Vision and Goals

### Primary Goals

| Goal | Status |
|------|--------|
| Keep Downloads folder clean automatically | ✅ |
| Reduce manual file management | ✅ |
| Maintain structured folder hierarchy | ✅ |
| Support future AI-assisted workflows | 🔜 Planned |
| Preserve user isolation on multi-user Macs | ✅ |
| Build foundation for a personal AI OS | 🔜 Planned |

### Long-Term Vision (v1.0)

A **Personal AI Operating System** combining:

- Autonomous file organization
- Personal knowledge management (Obsidian)
- Work tracking and weekly reporting
- Local-first AI assistance (Ollama, Hermes Agent)
- Agent-driven automation orchestration

---

## Repository Structure

```
personal-mac-automation/
├── configs/
│   └── download-rules.yaml       # Active rules configuration
├── docs/
│   ├── architecture.md           # High-level architecture
│   ├── downloads-automation.md   # Downloads feature overview
│   ├── roadmap.md                # Version roadmap
│   └── project-documentation.md  # This file
├── launchd/
│   └── com.ashwaq.downloadmanager.plist  # Monday 7 AM LaunchAgent
├── scripts/
│   └── download_manager.py       # Main automation script
├── tests/
│   ├── conftest.py               # Fixtures and helpers
│   └── test_download_manager.py  # 8 test cases
├── logs/                         # Runtime logs (gitignored)
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

### Folders Referenced but Not Yet in Repo

| Path | Purpose |
|------|---------|
| `ai/` | Future AI integration code |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     macOS (User Session)                        │
│                                                                 │
│  ┌──────────────┐    schedule     ┌──────────────────────────┐  │
│  │   launchd    │ ──────────────► │  download_manager.py     │  │
│  │ LaunchAgent  │   Mon 7 AM      │  (Automation Engine)     │  │
│  └──────────────┘                 └────────────┬─────────────┘  │
│                                                │                │
│                     ┌──────────────────────────┼────────────┐ │
│                     │                          ▼            │ │
│                     │  ┌─────────────────────────────────┐   │ │
│                     │  │  Rules Engine                   │   │ │
│                     │  │  configs/download-rules.yaml    │   │ │
│                     │  └─────────────────────────────────┘   │ │
│                     │                          │            │ │
│                     │          ┌───────────────┼───────────┐ │ │
│                     │          ▼               ▼           ▼ │ │
│                     │   ~/Downloads    ~/Media/...   ~/Downloads/ToReview
│                     │   AutoArchive    TrashLater              │ │
│                     └──────────────────────────────────────────┘ │
│                                                │                │
│                                                ▼                │
│                              logs/download-manager.log          │
└─────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **User-scoped execution** — Never touches other users' home directories
2. **Configuration-driven behavior** — Rules live in YAML, not Python
3. **Safe multi-stage file lifecycle** — Staged retention before deletion
4. **Git-managed platform** — Version-controlled automation as code
5. **Future AI extensibility** — Modular foundation for classification and agents
6. **Minimal system dependencies** — Python 3 + PyYAML + pytest (dev)

### Core Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Rules Engine | `configs/download-rules.yaml` | Retention periods, routing, dry-run |
| Automation Engine | `scripts/download_manager.py` | 3-stage scan, move, delete, log |
| Logging Layer | `logs/download-manager.log` | Audit trail for all operations |
| Scheduling Layer | `launchd/com.ashwaq.downloadmanager.plist` | Monday 7 AM via launchd |
| Test Suite | `tests/` | Isolated pytest coverage |
| Future AI Layer | `ai/` (planned) | Classification, Obsidian, agents |

---

## Downloads Automation Engine

### Entry Point

```bash
python scripts/download_manager.py
```

### Execution Flow

1. Load `configs/download-rules.yaml` (or `DOWNLOAD_RULES_CONFIG` override)
2. Read `settings.dry_run` (default: `true`)
3. Initialize logging to configured log file
4. **Stage 1:** Scan `~/Downloads` — route media, age-gate review/archive
5. **Stage 2:** Scan `~/Downloads/AutoArchive` — move to TrashLater when aged
6. **Stage 3:** Scan `~/Downloads/TrashLater` — delete when aged
7. Log finish; exit non-zero if any file operation failed

### Key Functions

| Function | Purpose |
|----------|---------|
| `load_config()` | Parse YAML; exit on missing/invalid config |
| `get_rule(config, item)` | Resolve rule by file extension |
| `route_downloads_file()` | Stage 1 routing and archive decisions |
| `process_staged_folder()` | Stage 2/3 threshold processing |
| `safe_move(src, dst_dir, dry_run)` | Collision-safe move with logging |
| `safe_delete(path, dry_run)` | Permanent delete with logging |
| `file_age_days(path)` | Calculate age from `st_mtime` |
| `process_downloads_folder()` | Iterate stage 1 files with error tracking |

### Routing Logic (Stage 1 Only)

```
For each file in ~/Downloads:
│
├─ rule.route == "media"
│   └─► Move to ~/Media/Videos/Incoming (immediate)
│
├─ rule.route == "media_assets"
│   └─► Move to ~/Media/Assets/Downloads (immediate)
│
├─ rule.route == "review"
│   ├─ age >= archive_after_days → Move to ~/Downloads/ToReview
│   └─ else → NO ACTION
│
├─ age >= archive_after_days (standard types)
│   └─► Move to ~/Downloads/AutoArchive
│
└─ else → NO ACTION
```

Stages 2 and 3 use `process_staged_folder()` with a single threshold each (`trash_after_days`, `delete_after_days`).

---

## Configuration Reference

**File:** `configs/download-rules.yaml`

### Settings

```yaml
settings:
  dry_run: true   # true = log/print only, no file changes
```

### Paths

| Key | Default | Used By Script |
|-----|---------|----------------|
| `downloads_dir` | `~/Downloads` | ✅ Stage 1 scan |
| `auto_archive_dir` | `~/Downloads/AutoArchive` | ✅ Stage 1 target / Stage 2 scan |
| `trash_later_dir` | `~/Downloads/TrashLater` | ✅ Stage 2 target / Stage 3 scan |
| `to_review_dir` | `~/Downloads/ToReview` | ✅ Review target |
| `media_incoming_dir` | `~/Media/Videos/Incoming` | ✅ Media target |
| `media_assets_dir` | `~/Media/Assets/Downloads` | ✅ Audio target |
| `log_file` | `~/Projects/personal-mac-automation/logs/download-manager.log` | ✅ |

### Per-Extension Rules

| Extension | Behavior |
|-----------|----------|
| `dmg`, `pkg` | Archive @ 3d → Trash @ 14d → Delete @ 30d |
| `zip` | Archive @ 7d → Trash @ 30d → Delete @ 60d |
| `pdf`, `docx`, `xlsx` | Archive @ 30d → Trash @ 90d → Delete @ 120d |
| `mp4`, `mov`, `mkv` | Immediate route → `media` (Videos/Incoming) |
| `mp3`, `wav` | Immediate route → `media_assets` |
| *(default)* | `route: review`; move to ToReview @ 14d |

### Rule Schema

```yaml
# Age-based lifecycle (per stage)
archive_after_days: <int>   # Stage 1 (Downloads)
trash_after_days: <int>     # Stage 2 (AutoArchive)
delete_after_days: <int>    # Stage 3 (TrashLater)

# Immediate routing (stage 1 only)
route: media | media_assets | review
```

### Test Override

```bash
DOWNLOAD_RULES_CONFIG=/path/to/test-rules.yaml pytest tests/ -v
```

---

## File Lifecycle and Routing

### Full Lifecycle

```
Stage 1 — Downloads
    ├─ media / media_assets → immediate routing
    ├─ review (default) → ToReview when aged
    └─ standard → AutoArchive when aged

Stage 2 — AutoArchive → TrashLater when aged

Stage 3 — TrashLater → permanent delete when aged
```

### Media Workflow

```
Downloads ──► Media/Videos/Incoming     (video: mp4, mov, mkv)
Downloads ──► Media/Assets/Downloads    (audio: mp3, wav)
```

### Review Workflow

```
Downloads ──► Downloads/ToReview        (unknown extensions, age >= 14d)
```

### Recovery Windows

| Stage | Purpose |
|-------|---------|
| **Downloads** | Active working area for new downloads |
| **AutoArchive** | First staging area; files still recoverable |
| **TrashLater** | Final staging before permanent deletion |
| **ToReview** | Manual inspection for unrecognized types |
| **Delete** | Permanent removal (no trash bin — `unlink()`) |

---

## Personal Folder Hierarchy

Beyond the automation project, the platform assumes a structured home directory:

### Projects

```
~/Projects/
├── Active/
├── Learning/
├── Ideas/
├── Experiments/
├── Completed/
└── personal-mac-automation/    ← this repo
```

### Notes

```
~/Notes/ObsidianVault/
```

### Media

```
~/Media/
├── Videos/
│   ├── Incoming/       ← video downloads routed here
│   ├── ToSort/
│   ├── Raw/
│   └── Final/
├── Photos/
├── ScreenRecordings/
├── Audio/
├── Exports/
└── Assets/
    └── Downloads/      ← audio downloads routed here
```

### Documents

```
~/Documents/
├── Finance/
├── Insurance/
├── Travel/
├── Certificates/
├── Purchases/
└── Family/
```

### Archive

```
~/Archive/
├── Projects/
├── Documents/
├── Media/
└── Downloads/
```

### Downloads Workflow Folders

```
~/Downloads/
├── AutoArchive/
├── TrashLater/
└── ToReview/
```

---

## Runtime and Scheduling

### Manual Execution

```bash
cd ~/Projects/personal-mac-automation
source .venv/bin/activate
python scripts/download_manager.py
```

### LaunchAgent

Repository plist: `launchd/com.ashwaq.downloadmanager.plist`

**Schedule:** Every Monday at 7:00 AM.

```bash
cp launchd/com.ashwaq.downloadmanager.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist
launchctl list | grep downloadmanager
```

Stdout/stderr: `logs/launchd-stdout.log`, `logs/launchd-stderr.log`

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyYAML | 6.0.3 | YAML config parsing |
| pytest | 8.4.1 | Test suite (dev) |

Python standard library: `pathlib`, `datetime`, `shutil`, `logging`.

---

## Logging and Observability

**Log file:** `~/Projects/personal-mac-automation/logs/download-manager.log`

### Log Event Types

| Event | Example |
|-------|---------|
| Start/finish | `Download manager started. dry_run=True` |
| Move | `MOVE /Users/.../file.zip -> /Users/.../AutoArchive/file.zip` |
| Delete | `DELETE /Users/.../old.dmg` |
| Dry run | `DRY_RUN MOVE ...` / `DRY_RUN DELETE ...` |
| No action | `NO ACTION /path/file ext=txt age_days=2.50` |
| Error | `Failed to process /path/file: ...` |

### Troubleshooting

| Symptom | Check |
|---------|-------|
| Files not moving | `settings.dry_run` must be `false` |
| No log output | Ensure log directory exists; check permissions |
| LaunchAgent not running | `launchctl list \| grep downloadmanager` |
| Script errors | Run manually with venv activated; check exit code |

---

## Security and Multi-User Model

### User Isolation

All paths resolve through `Path.home()` and `expanduser()`. The automation:

- ✅ Operates only in the executing user's home directory
- ✅ Does not require root or system-wide installation
- ✅ Is safe on shared Macs (separate home dirs per user)

### Deletion Behavior

`safe_delete()` uses `path.unlink()` — files are **permanently deleted**, not sent to macOS Trash.

---

## Development Setup

### Prerequisites

- macOS
- Python 3
- Git

### Initial Setup

```bash
cd ~/Projects/personal-mac-automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Testing

```bash
pytest tests/ -v
```

Tests use isolated temp directories via `DOWNLOAD_RULES_CONFIG`.

### Production Promotion

1. Run tests — all pass
2. Run with `dry_run: true`, inspect log
3. Set `dry_run: false` in yaml
4. Run once manually, verify moves
5. Load LaunchAgent plist

---

## Known Limitations and Gaps

| # | Limitation | Impact | Suggested Fix |
|---|------------|--------|---------------|
| 1 | No config validation | Typos fail at runtime | Add schema validation (v0.2) |
| 2 | No duplicate detection | Same file re-downloaded stays | Planned v0.2 |
| 3 | Direct `unlink()` delete | No macOS Trash recovery | Consider `send2trash` or move to Trash |
| 4 | Age based on `mtime` only | Download date ≠ modification date | Consider `st_birthtime` on macOS |
| 5 | Flat directory scan only | Subfolders in Downloads ignored | Document or add recursive option |

---

## Roadmap

### v0.1 — ✅ Completed

- Downloads automation framework
- YAML configuration, logging, media/review routing
- User isolation, GitHub repository

### v0.1.1 — ✅ Completed

- Full 3-stage pipeline
- Age-gated review routing
- pytest suite, LaunchAgent plist in repo
- Collision-safe moves, error handling

### v0.2 — Planned

- Configuration validation
- Duplicate file detection
- Archive reporting and retention analytics

### v0.3+ — Planned

- Obsidian integration, local AI, Hermes Agent
- Personal AI Operating System (v1.0)

---

## Git History

| Commit | Description |
|--------|-------------|
| `89f01c5` | Add detailed README for mac automation toolkit |
| `078a6c3` | Initial automation platform |
| `489288f` | Add project documentation |
| `cf66b36` | Hygiene Tasks |
| `3ab4ad8` | Enhance README with architecture and roadmap |

---

## Quick Reference Card

```bash
# Activate environment
source ~/Projects/personal-mac-automation/.venv/bin/activate

# Run tests
pytest tests/ -v

# Dry-run (default dry_run: true)
python ~/Projects/personal-mac-automation/scripts/download_manager.py

# View recent log entries
tail -50 ~/Projects/personal-mac-automation/logs/download-manager.log

# Edit rules
$EDITOR ~/Projects/personal-mac-automation/configs/download-rules.yaml

# Install scheduler
cp launchd/com.ashwaq.downloadmanager.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist
```

---

*This document consolidates information from `README.md`, `docs/architecture.md`, `docs/downloads-automation.md`, `docs/roadmap.md`, and direct source code analysis.*
