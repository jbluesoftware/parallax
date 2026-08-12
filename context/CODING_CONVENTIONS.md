# Coding Conventions: parallax

Short and sharp. If it's not here, match the surrounding code.

## General

- No dead code, no commented-out blocks — delete instead of commenting out.
- No `console.log`/`print` debugging left in committed code.
- Prefer explicit over clever. Optimize for the next agent reading this, not line count.
- Every function does one thing. Split it if you need "and" to describe it.

## Python (backend)

- Format with `black`, lint with `ruff`. Run both before considering a change done.
- Type hints on every function signature.
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Use Pydantic models for all API request/response shapes — no raw dicts crossing the API boundary.
- Routes (`app/api/`) contain no logic — they call `app/core/` and return. If a route has an `if`/`for` beyond input validation, that logic belongs in `core/`.
- Catch exceptions at the boundary (routes), not deep in `core/` — let `core/` raise, let routes translate to the error format in `API_CONTRACT.md`.
- Async endpoints (`async def`) unless there's a specific reason not to.

## JavaScript / React (frontend)

- `PascalCase` for components and their files (`AgentCard.jsx`), `camelCase` for functions/variables, `kebab-case` for CSS classes.
- Functional components + hooks only. No class components.
- One component per file, default export.
- `components/` receive data via props only — no `fetch`/`api/` calls inside them. Data-fetching lives in `pages/`.
- Destructure props in the function signature: `function AgentCard({ agent, onStart })`, not `props.agent`.
- No inline arrow functions in JSX for anything non-trivial — name it above the `return`.
- All API calls go through `frontend/src/api/` — never `fetch` directly in a component or page.

## Naming

- Match `API_CONTRACT.md` field names exactly — backend `snake_case` JSON keys are not renamed on the way into the frontend.
- Booleans read as questions: `isRunning`, `hasError`, not `running`, `error_flag`.
- No abbreviations beyond common ones (`id`, `config`, `msg` are fine; `agnt`, `mgr` are not).

## Comments

- Comment *why*, not *what*. `# retry because agent socket drops after idle timeout`, not `# retry the request`.
- No comment is better than a stale or obvious one.

## Commits (if applicable)

- One logical change per commit.
- Message format: `<area>: <what changed>` — e.g. `backend: add agent stop endpoint`, `frontend: fix agent card hover state`.