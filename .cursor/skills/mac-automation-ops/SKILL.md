---
name: mac-automation-ops
description: Deploy, run, and troubleshoot personal-mac-automation on macOS. Use when setting up a fresh laptop, installing LaunchAgent, enabling production mode, checking logs, running download_manager.py manually, or diagnosing yaml/venv/LaunchAgent issues.
---

# Mac Automation — Operations

## Fresh laptop setup

```bash
git clone git@github.com:ashwaqar/personal-mac-automation.git ~/Projects/personal-mac-automation
cd ~/Projects/personal-mac-automation
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_manager.py   # bootstraps all folders automatically
```

First run creates automation paths + all `bootstrap_dirs` from config.

## Production checklist

1. `.venv/bin/pytest tests/ -v` — all pass
2. Set `dry_run: true`, run script, inspect `logs/download-manager.log`
3. Set `dry_run: false` in `configs/download-rules.yaml`
4. Run once manually: `.venv/bin/python scripts/download_manager.py`
5. Install LaunchAgent (below)

## LaunchAgent

```bash
cp launchd/com.ashwaq.downloadmanager.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.ashwaq.downloadmanager.plist
launchctl list | grep downloadmanager
```

- Schedule: **Monday 7:00 AM**
- Logs: `logs/launchd-stdout.log`, `logs/launchd-stderr.log`
- Uses: `.venv/bin/python` + absolute script path

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No module named 'yaml'` | Use `.venv/bin/python`, not bare `python3` |
| Files not moving | Check `settings.dry_run` is `false` |
| Config errors on start | Fix YAML; check `logs/download-manager.log` |
| LaunchAgent not running | `launchctl list \| grep downloadmanager`; check stderr log |
| Script exits 1 | Per-file errors logged; check permissions/locked files |

## Safe testing

```yaml
settings:
  dry_run: true
```

Dry-run logs `DRY_RUN MOVE`, `DRY_RUN DELETE`, `DRY_RUN DUPLICATE` without changing files.

## Logs

```bash
tail -50 ~/Projects/personal-mac-automation/logs/download-manager.log
```
