# Development reference

## Core functions

| Function | File stage |
|----------|------------|
| `load_config()` | Read YAML from `DOWNLOAD_RULES_CONFIG` or default path |
| `validate_config()` | Return list of error strings |
| `ensure_workspace()` | Create `paths` dirs + `bootstrap_dirs` |
| `route_downloads_file()` | Stage 1: Downloads |
| `process_staged_folder()` | Stages 2–3 |
| `safe_move()` / `safe_delete()` | File ops with logging |
| `find_content_duplicate()` | Same name + size + hash in dest |

## Personal folder hierarchy (`bootstrap_dirs`)

```text
~/Projects/{Active,Learning,Ideas,Experiments,Completed}
~/Notes/ObsidianVault
~/Media/Videos/{Incoming,ToSort,Raw,Final}
~/Media/{Photos,ScreenRecordings,Audio,Exports}
~/Media/Assets/Downloads
~/Documents/{Finance,Insurance,Travel,Certificates,Purchases,Family}
~/Archive/{Projects,Documents,Media,Downloads}
~/Downloads/{AutoArchive,TrashLater,ToReview}
```

## Dependencies

- `PyYAML==6.0.3`
- `pytest>=8.0.0` (dev/test)

## Planned (v0.2 remainder)

- Archive reporting script
- Retention analytics
