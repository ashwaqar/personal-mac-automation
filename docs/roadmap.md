# Roadmap

## Vision

Build a personal automation and AI platform for macOS that combines:

* File management
* Knowledge management
* AI assistance
* Productivity automation

## Version 0.1

Completed

### Features

* Downloads automation
* YAML configuration
* Logging
* LaunchAgent scheduling
* Media routing
* Review routing
* User isolation

---

## Version 0.1.1

Completed

### Pipeline and Hardening

* Restored full 3-stage pipeline (Downloads → AutoArchive → TrashLater → Delete)
* Age-gated review routing for unknown file types
* Error handling with non-zero exit on failures
* Collision-safe file moves
* `dry_run: true` safe default

### Repository

* pytest test suite (`tests/`)
* LaunchAgent plist in repo (`launchd/com.ashwaq.downloadmanager.plist`, Monday 7 AM)
* Documentation aligned with implemented behavior

---

## Version 0.2

In progress

### Completed

* Configuration validation on startup
* Duplicate file detection (SHA-256 content hash)
* Workspace bootstrap (`ensure_workspace`, `bootstrap_dirs`)

### Planned

* Archive reporting
* Retention analytics
* Release process improvements

---

## Version 0.3

Planned

### Obsidian Integration

* Daily note automation
* Project note creation
* Knowledge organization

### Reporting

* Weekly activity reports
* Monthly summaries

---

## Version 0.4

Planned

### Local AI Integration

* Ollama integration
* Local model evaluation
* File classification

### AI Use Cases

* Document categorization
* Download routing suggestions
* Knowledge extraction

---

## Version 0.5

Planned

### Hermes Agent Integration

* Local agent workflows
* File management actions
* Knowledge management actions
* Productivity workflows

---

## Version 1.0

Personal AI Operating System

### Capabilities

* Autonomous file organization
* Personal knowledge management
* Work tracking
* Weekly reporting
* AI-assisted productivity
* Local-first execution
