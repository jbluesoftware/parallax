# Project Structure: parallax

Python/tkinter desktop dashboard for monitoring and controlling AI agents on macOS.

## Purpose of this file

This document describes the codebase layout and the responsibility of each directory/file. Read this first before navigating or editing the codebase.

## Architecture principle

UI code (`app/ui/`) and business logic (`app/core/`) are strictly separated. UI code never talks to agents directly — it calls into `app/core/`, which handles process management, API calls, and polling. This keeps the UI layer swappable and the logic layer testable/reusable independent of tkinter.

## Directory tree

```
parallax/
├── main.py
├── requirements.txt
├── app/
│   ├── config.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── theme.py
│   │   └── widgets/
│   │       ├── agent_card.py
│   │       ├── log_panel.py
│   │       ├── metrics_chart.py
│   │       └── sidebar.py
│   ├── core/
│   │   ├── agent_manager.py
│   │   ├── agent_client.py
│   │   └── scheduler.py
│   ├── models/
│   │   └── agent.py
│   └── storage/
│       └── persistence.py
├── assets/
│   ├── icons/
│   └── fonts/
├── tests/
│   ├── test_agent_manager.py
│   └── test_persistence.py
└── build/
    ├── build.spec
    └── build.sh
```

## File and folder reference

### Root

| Path | Purpose |
|---|---|
| `main.py` | Entry point. Creates the tkinter root window and launches the main App class from `app/ui/main_window.py`. Run with `python3 main.py`. |
| `requirements.txt` | Python package dependencies (e.g. `customtkinter`, `requests`, `matplotlib`). |

### `app/`

Top-level Python package containing all application source code.

| Path | Purpose |
|---|---|
| `app/config.py` | Global constants and settings: API URLs, refresh/polling intervals, file paths, default values. Single source of truth for configuration — no hardcoded values elsewhere. |

### `app/ui/`

All visual/presentation code. Contains tkinter (or customtkinter) window and widget definitions. Should contain **no** direct agent communication logic — only calls into `app/core/`.

| Path | Purpose |
|---|---|
| `app/ui/main_window.py` | Root application window/class. Defines overall layout (sidebar, main panel) and instantiates widgets. |
| `app/ui/theme.py` | Shared visual constants: colors, fonts, spacing, padding. Import from here rather than hardcoding style values in widgets. |
| `app/ui/widgets/agent_card.py` | Reusable widget displaying a single agent's status (name, state, key metrics). |
| `app/ui/widgets/log_panel.py` | Scrolling panel for displaying agent logs/output in real time. |
| `app/ui/widgets/metrics_chart.py` | Embedded chart widget (matplotlib/plotly) for visualizing agent metrics over time. |
| `app/ui/widgets/sidebar.py` | Navigation/agent-list sidebar widget. |

### `app/core/`

Non-visual application logic. This is the layer that actually interacts with agents. Independent of tkinter — could be reused with a different UI framework.

| Path | Purpose |
|---|---|
| `app/core/agent_manager.py` | Manages local agent process lifecycle: start, stop, restart, and monitor agent subprocesses. |
| `app/core/agent_client.py` | HTTP/WebSocket client for communicating with agents that run as remote/local services (as opposed to local subprocesses). |
| `app/core/scheduler.py` | Background polling/refresh loop. Since tkinter's mainloop is single-threaded, this handles periodic agent-status updates via a background thread or `root.after()`, without blocking the UI. |

### `app/models/`

Plain data structures shared across the app. No logic beyond basic validation/serialization.

| Path | Purpose |
|---|---|
| `app/models/agent.py` | Data class representing an agent (id, name, status, metrics, last-updated timestamp, etc.). Used by both `core/` and `ui/`. |

### `app/storage/`

Local persistence layer.

| Path | Purpose |
|---|---|
| `app/storage/persistence.py` | Save/load application state to disk (JSON or SQLite) — e.g. agent list, dashboard settings, historical metrics. |

### `assets/`

Static, non-code resources.

| Path | Purpose |
|---|---|
| `assets/icons/` | App and UI icons (e.g. `.png`, `.icns` for macOS app icon). |
| `assets/fonts/` | Custom font files, if not relying on system fonts. |

### `tests/`

Unit tests, mirroring the `app/core/` and `app/storage/` modules. UI code is generally not unit tested directly.

| Path | Purpose |
|---|---|
| `tests/test_agent_manager.py` | Tests for `app/core/agent_manager.py`. |
| `tests/test_persistence.py` | Tests for `app/storage/persistence.py`. |

### `build/`

Packaging configuration, kept separate from source code.

| Path | Purpose |
|---|---|
| `build/build.spec` | PyInstaller spec file defining how to bundle the app into a macOS `.app`. |
| `build/build.sh` | Shell script to run the packaging/build process. |

## Conventions for AI agents editing this codebase

- New UI components go in `app/ui/widgets/`, one class per file.
- New agent-communication logic goes in `app/core/`, not `app/ui/`.
- New shared data structures go in `app/models/`.
- Never hardcode colors/fonts in widget files — reference `app/ui/theme.py`.
- Never hardcode config values (URLs, intervals) — reference `app/config.py`.
- Each `app/` subpackage should have an `__init__.py` (already present) to remain importable.