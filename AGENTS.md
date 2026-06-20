# Agent Guide — personal-mac-automation

> Read this first when working in this repository on any machine or Cursor account.

## What this project is

Git-backed **macOS personal automation platform** (Python 3, PyYAML, launchd). Current focus: **Downloads folder manager** with a 3-stage lifecycle, media routing, config validation, duplicate detection, and workspace bootstrap.

**Version:** v0.2.1  
**Repo:** `git@github.com:ashwaqar/personal-mac-automation.git`  
**Runtime:** User-scoped only (`Path.home()`). Never touch other users' home directories.

## Repository layout

```text
scripts/download_manager.py   # Main automation engine
configs/download-rules.yaml   # Rules, paths, bootstrap dirs, settings
launchd/*.plist               # Monday 7 AM LaunchAgent template
tests/                        # pytest suite (28+ tests)
docs/                         # Architecture, roadmap, full reference
logs/                         # Runtime logs (gitignored)
.cursor/rules/                # Cursor rules (auto-loaded)
.cursor/skills/               # Cursor skills (project workflows)
```

## Critical runtime rules

1. **Always use the project venv** — bare `python3` (e.g. Homebrew) lacks PyYAML/pytest:
   ```bash
   source .venv/bin/activate
   # or: .venv/bin/python scripts/download_manager.py
   ```
2. **Config override for tests:** `DOWNLOAD_RULES_CONFIG=/path/to/yaml`
3. **Never commit secrets** — no `.env`, credentials, or personal log contents
4. **Only commit when the user explicitly asks**

## 3-stage pipeline (must preserve semantics)

| Stage | Folder | Action |
|-------|--------|--------|
| 1 | `~/Downloads` | Route media immediately; age-gated review → ToReview; aged files → AutoArchive |
| 2 | `~/Downloads/AutoArchive` | Move to TrashLater when `trash_after_days` exceeded |
| 3 | `~/Downloads/TrashLater` | Permanent delete when `delete_after_days` exceeded |

Each age threshold applies **only in its stage folder** — never all three on Downloads in one pass.

## Key functions (`scripts/download_manager.py`)

| Function | Purpose |
|----------|---------|
| `validate_config()` | Startup YAML validation; abort on errors |
| `ensure_workspace()` | Create automation + `bootstrap_dirs` folders |
| `route_downloads_file()` | Stage 1 routing only |
| `process_staged_folder()` | Stages 2 and 3 |
| `find_content_duplicate()` | Same filename + size + SHA-256 in destination |

## Config settings (`configs/download-rules.yaml`)

```yaml
settings:
  dry_run: false              # true = log only, no file changes
  duplicate_detection: true   # remove re-downloads (same name + content)
  bootstrap_folders: true     # create missing dirs on startup
```

## Development workflow

```bash
cd ~/Projects/personal-mac-automation
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
python scripts/download_manager.py
```

After code changes: run full test suite before claiming success.

## LaunchAgent (production)

```bash
cp launchd/com.ashwaq.downloadmanager.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist
launchctl list | grep downloadmanager
```

Schedule: **Monday 7:00 AM**. Uses `.venv/bin/python` from repo path.

## Coding conventions

- Minimize scope — focused diffs, no unrelated changes
- Match existing style: plain functions, minimal deps, no over-abstraction
- Config-driven behavior — new file types go in YAML, not Python
- Add tests for new behavior in `tests/`
- Update `CHANGELOG.md` for user-facing changes

## Documentation map

| Doc | Use when |
|-----|----------|
| [README.md](README.md) | Setup, features, troubleshooting |
| [docs/project-documentation.md](docs/project-documentation.md) | Full technical reference |
| [docs/architecture.md](docs/architecture.md) | System design |
| [docs/roadmap.md](docs/roadmap.md) | Version planning |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

## Cursor-specific assets

- **Rules:** `.cursor/rules/*.mdc` — auto-applied context
- **Skills:** `.cursor/skills/mac-automation-dev/` and `mac-automation-ops/` — invoke for dev or ops tasks

## Roadmap (next planned)

- v0.2 remainder: archive reporting, retention analytics
- v0.3: Obsidian integration, weekly/monthly reports
- v0.4+: Local AI (Ollama), file classification, Hermes Agent
