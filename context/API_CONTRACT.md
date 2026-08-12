# API Contract: parallax

Defines every REST endpoint exposed by the FastAPI backend and consumed by the React frontend. This is the source of truth for request/response shapes — `frontend/src/api/agents.js` and `backend/app/api/*.py` must both match what's defined here. If you change an endpoint, update this file in the same change.

## Conventions

- Base URL (local dev): `http://localhost:8000`
- All request/response bodies are JSON.
- All timestamps are ISO 8601 strings, UTC (e.g. `"2026-08-12T14:30:00Z"`).
- Errors follow a consistent shape (see [Error format](#error-format)) with an appropriate HTTP status code.
- No authentication at this stage (local-only tool). Add a note here before introducing auth.

## Agent status enum

Used across multiple endpoints. Canonical values — do not introduce new ones without updating this file and `backend/app/models/agent.py`.

```
"running" | "idle" | "error" | "stopped"
```

| Value | Meaning | UI status color (see STYLE_GUIDE.md) |
|---|---|---|
| `running` | Agent is actively working | `--status-success` |
| `idle` | Agent is alive, waiting for input/trigger | `--status-warning` |
| `error` | Agent hit an error and is not running | `--status-error` |
| `stopped` | Agent process is not running (intentionally) | `--text-secondary` (neutral, no status color) |

## Endpoints

### `GET /agents`

List all agents and their current status. Used by `Dashboard.jsx` via `usePolling`.

**Response `200`**

```json
{
  "agents": [
    {
      "id": "agent_01",
      "name": "Research Agent",
      "status": "running",
      "last_active": "2026-08-12T14:30:00Z",
      "metrics": {
        "tasks_completed": 12,
        "avg_response_time_ms": 842,
        "error_count": 0
      }
    }
  ]
}
```

---

### `GET /agents/{agent_id}`

Full detail for a single agent. Used by `AgentDetail.jsx`.

**Response `200`** — same shape as one item in `GET /agents`, plus:

```json
{
  "id": "agent_01",
  "name": "Research Agent",
  "status": "running",
  "last_active": "2026-08-12T14:30:00Z",
  "created_at": "2026-08-01T09:00:00Z",
  "metrics": {
    "tasks_completed": 12,
    "avg_response_time_ms": 842,
    "error_count": 0
  },
  "config": {
    "type": "subprocess",
    "command": "python agents/research_agent.py"
  }
}
```

**Response `404`** — agent ID not found (see [Error format](#error-format)).

---

### `POST /agents/{agent_id}/start`

Start a stopped agent. Used by the "Start" action on `AgentCard.jsx`.

**Response `200`**

```json
{ "id": "agent_01", "status": "running" }
```

**Response `409`** — agent already running.
**Response `404`** — agent ID not found.

---

### `POST /agents/{agent_id}/stop`

Stop a running agent.

**Response `200`**

```json
{ "id": "agent_01", "status": "stopped" }
```

**Response `409`** — agent already stopped.
**Response `404`** — agent ID not found.

---

### `GET /agents/{agent_id}/logs`

Fetch recent log lines for an agent. Used by `LogPanel.jsx` via polling.

**Query params**

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | `100` | Max number of log lines to return, most recent first |
| `since` | string (ISO 8601) | none | Only return logs after this timestamp (optional, for incremental polling) |

**Response `200`**

```json
{
  "agent_id": "agent_01",
  "logs": [
    { "timestamp": "2026-08-12T14:29:58Z", "level": "info", "message": "Task started" },
    { "timestamp": "2026-08-12T14:30:00Z", "level": "error", "message": "Timeout connecting to tool" }
  ]
}
```

`level` is one of: `"info" | "warning" | "error"`.

---

### `GET /agents/{agent_id}/metrics`

Time-series metrics for `MetricsChart.jsx`.

**Query params**

| Param | Type | Default | Description |
|---|---|---|---|
| `range` | string | `"1h"` | One of `"1h" \| "24h" \| "7d"` |

**Response `200`**

```json
{
  "agent_id": "agent_01",
  "range": "1h",
  "points": [
    { "timestamp": "2026-08-12T14:00:00Z", "tasks_completed": 3, "avg_response_time_ms": 810 },
    { "timestamp": "2026-08-12T14:15:00Z", "tasks_completed": 5, "avg_response_time_ms": 790 }
  ]
}
```

## Error format

All non-2xx responses use this shape:

```json
{
  "error": {
    "code": "agent_not_found",
    "message": "No agent with id 'agent_99'"
  }
}
```

| HTTP status | `code` | When |
|---|---|---|
| `404` | `agent_not_found` | Agent ID doesn't exist |
| `409` | `agent_already_running` | Start called on a running agent |
| `409` | `agent_already_stopped` | Stop called on a stopped agent |
| `500` | `internal_error` | Unhandled backend error |

Frontend `api/` functions should throw on non-2xx and surface `error.message` to the UI (see empty/error state rules in `STYLE_GUIDE.md`) — never a raw stack trace or unhandled promise rejection.

## Polling intervals

Defined once in `backend/app/config.py` (backend refresh rate) and frontend polling hook usage (`usePolling`) — must stay in sync:

| Data | Interval |
|---|---|
| Agent list (`GET /agents`) | 5s |
| Agent detail (`GET /agents/{id}`) | 3s |
| Logs (`GET /agents/{id}/logs`) | 3s |
| Metrics (`GET /agents/{id}/metrics`) | 10s |

## Adding a new endpoint

1. Add it to this file first — path, method, request/response shape, error cases.
2. Implement the route in `backend/app/api/`, calling into `backend/app/core/`.
3. Add the corresponding function to `frontend/src/api/agents.js`.
4. Never let frontend and backend field names drift (e.g. `taskCount` vs `tasks_completed`) — this file is the tiebreaker; backend uses `snake_case` JSON keys throughout, matched exactly in frontend consumption.