# Project Structure: parallax

Web-based dashboard for monitoring and controlling AI agents. React frontend (browser-only, no desktop wrapper), FastAPI backend. Backend exposes agent logic over a REST API; frontend polls periodically for updates.

## Purpose of this file

Describes the codebase layout and the responsibility of each directory/file. Read this before navigating or editing the codebase.

## Architecture principle

Frontend and backend are fully separate processes communicating over HTTP. The frontend holds **no** agent logic — it only calls backend REST endpoints and renders responses. The backend holds **no** UI/rendering logic — it only exposes agent state and actions as JSON. This split means either side can be rebuilt independently.

Data flow: `React component → api/ client function → FastAPI route → app/core/ logic → agent`. Live updates use **periodic polling** (not WebSockets) — components re-fetch on an interval via a shared polling hook, not a persistent connection.

## Directory tree

```
parallax/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   └── agents.js
│       ├── components/
│       │   ├── AgentCard.jsx
│       │   ├── LogPanel.jsx
│       │   ├── MetricsChart.jsx
│       │   ├── Sidebar.jsx
│       │   └── StatusDot.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   └── AgentDetail.jsx
│       ├── hooks/
│       │   └── usePolling.js
│       ├── styles/
│       │   ├── variables.css
│       │   ├── global.css
│       │   └── components/
│       │       ├── AgentCard.css
│       │       ├── LogPanel.css
│       │       └── Sidebar.css
│       └── utils/
│           └── format.js
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── config.py
│       ├── api/
│       │   ├── routes_agents.py
│       │   └── routes_logs.py
│       ├── core/
│       │   ├── agent_manager.py
│       │   ├── agent_client.py
│       │   └── scheduler.py
│       ├── models/
│       │   └── agent.py
│       └── storage/
│           └── persistence.py
│   └── tests/
│       ├── test_agent_manager.py
│       └── test_persistence.py
│
└── context/
    ├── PROJECT_STRUCTURE.md
    └── STYLE_GUIDE.md
```

## File and folder reference

### `frontend/`

React application (built with Vite). Browser-only — no Tauri/Electron wrapper at this stage.

| Path | Purpose |
|---|---|
| `frontend/index.html` | HTML entry point Vite injects the React app into. |
| `frontend/package.json` | Frontend dependencies and scripts (`dev`, `build`). |
| `frontend/vite.config.js` | Vite build/dev-server configuration, including backend proxy setup for local development. |
| `frontend/src/main.jsx` | React entry point — mounts `App.jsx` into the DOM. |
| `frontend/src/App.jsx` | Root component. Defines routing/layout (sidebar + page content) and top-level polling setup. |

#### `frontend/src/api/`

All backend communication lives here. Components never call `fetch`/`axios` directly.

| Path | Purpose |
|---|---|
| `frontend/src/api/agents.js` | Functions for calling agent-related backend endpoints (`getAgents`, `startAgent`, `stopAgent`, `getAgentLogs`, etc.). Returns parsed JSON, throws on error. |

#### `frontend/src/components/`

Reusable, presentational UI pieces. One component per file. Components receive data via props — they don't fetch data themselves (pages do that and pass it down).

| Path | Purpose |
|---|---|
| `frontend/src/components/AgentCard.jsx` | Displays a single agent: status dot, name, key metrics, action buttons. |
| `frontend/src/components/LogPanel.jsx` | Scrollable panel rendering agent log lines. |
| `frontend/src/components/MetricsChart.jsx` | Chart component visualizing agent metrics over time. |
| `frontend/src/components/Sidebar.jsx` | Navigation sidebar listing agents/sections. |
| `frontend/src/components/StatusDot.jsx` | Small colored status indicator, reused across `AgentCard` and elsewhere. Single source of truth for status → color mapping. |

#### `frontend/src/pages/`

Top-level views mapped to routes/sections. Pages own data-fetching (via `api/` + `hooks/usePolling`) and pass data down to `components/`.

| Path | Purpose |
|---|---|
| `frontend/src/pages/Dashboard.jsx` | Main view — grid/list of all `AgentCard`s. |
| `frontend/src/pages/AgentDetail.jsx` | Detail view for a single agent — logs, metrics, controls. |

#### `frontend/src/hooks/`

Shared React hooks.

| Path | Purpose |
|---|---|
| `frontend/src/hooks/usePolling.js` | Generic polling hook: takes a fetch function and interval, returns latest data + loading/error state. Used by pages instead of each rolling its own `setInterval`. |

#### `frontend/src/styles/`

Plain CSS, no CSS-in-JS or Tailwind. See `STYLE_GUIDE.md` for full conventions.

| Path | Purpose |
|---|---|
| `frontend/src/styles/variables.css` | CSS custom properties: colors, spacing, radius, typography, transitions. Single source of truth — imported globally. |
| `frontend/src/styles/global.css` | Base/reset styles, body defaults, typography defaults. |
| `frontend/src/styles/components/*.css` | One CSS file per component, named to match (e.g. `AgentCard.jsx` → `AgentCard.css`). Imported directly in the matching component file. |

#### `frontend/src/utils/`

| Path | Purpose |
|---|---|
| `frontend/src/utils/format.js` | Formatting helpers (timestamps, durations, numbers) shared across components. |

### `backend/`

FastAPI application exposing agent logic as a REST API.

| Path | Purpose |
|---|---|
| `backend/main.py` | FastAPI app entry point. Creates the app instance, registers routers, configures CORS for local frontend dev. Run with `uvicorn main:app --reload`. |
| `backend/requirements.txt` | Backend Python dependencies (`fastapi`, `uvicorn`, etc.). |
| `backend/app/config.py` | Global settings: polling intervals, storage paths, CORS origins. Single source of truth for backend configuration. |

#### `backend/app/api/`

Route definitions only — no business logic. Routes call into `app/core/` and return responses.

| Path | Purpose |
|---|---|
| `backend/app/api/routes_agents.py` | Endpoints for listing agents, getting status, start/stop actions. |
| `backend/app/api/routes_logs.py` | Endpoints for fetching agent log output. |

#### `backend/app/core/`

Business logic. No FastAPI/HTTP-specific code here — this layer is framework-agnostic and could be reused outside the API.

| Path | Purpose |
|---|---|
| `backend/app/core/agent_manager.py` | Manages local agent process lifecycle: start, stop, restart, monitor subprocesses. |
| `backend/app/core/agent_client.py` | Client for communicating with agents running as separate services (if applicable). |
| `backend/app/core/scheduler.py` | Background refresh logic — periodically updates agent status/metrics so API reads are fast (not blocking on live agent calls). |

#### `backend/app/models/`

| Path | Purpose |
|---|---|
| `backend/app/models/agent.py` | Pydantic models for agent data — used for both internal state and API request/response schemas. |

#### `backend/app/storage/`

| Path | Purpose |
|---|---|
| `backend/app/storage/persistence.py` | Save/load state to disk (JSON or SQLite) — agent configs, historical metrics. |

#### `backend/tests/`

| Path | Purpose |
|---|---|
| `backend/tests/test_agent_manager.py` | Tests for `app/core/agent_manager.py`. |
| `backend/tests/test_persistence.py` | Tests for `app/storage/persistence.py`. |

### `context/`

This folder. Contains reference documents for AI agents working on the codebase — not application code.

| Path | Purpose |
|---|---|
| `context/PROJECT_STRUCTURE.md` | This file. |
| `context/STYLE_GUIDE.md` | Visual/UI conventions for the frontend. |

## Conventions for AI agents editing this codebase

- New UI pieces go in `frontend/src/components/` (reusable) or `frontend/src/pages/` (route-level), never both mixed in one file.
- Components do not fetch data directly — data-fetching happens in `pages/` via `api/` + `usePolling`, then passed down as props.
- New backend endpoints go in `backend/app/api/`; the actual logic they call goes in `backend/app/core/` — routes stay thin.
- Every component gets its own CSS file in `frontend/src/styles/components/`, named to match. No inline `style={}` props except for dynamic values that genuinely can't be a CSS class (see `STYLE_GUIDE.md`).
- Never hardcode colors, spacing, or radius values — use the CSS custom properties defined in `frontend/src/styles/variables.css`.
- Never hardcode config values (API base URL, polling intervals) — reference `backend/app/config.py` on the backend and a single frontend config constant (see `STYLE_GUIDE.md` / future `frontend/src/config.js` if introduced).