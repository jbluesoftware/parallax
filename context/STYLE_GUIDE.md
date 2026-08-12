# UI Style Guide: parallax

Visual and interaction standards for the parallax dashboard frontend (React + plain CSS). Read this before writing or editing any file in `frontend/src/components/`, `frontend/src/pages/`, or `frontend/src/styles/`.

## Design direction

Clean, modern, minimal. Muted color palette, generous whitespace, rounded corners, minimal outline-style icons, subtle motion. Every screen should be understandable at a glance, with no clutter and no unexplained controls.

## Styling approach: plain CSS with custom properties

No Tailwind, no CSS-in-JS, no component libraries. Use plain `.css` files with CSS custom properties (variables) as the single source of design tokens. Every component imports its own CSS file directly:

```jsx
// AgentCard.jsx
import "../styles/components/AgentCard.css";

export default function AgentCard({ agent }) {
  return <div className="agent-card">...</div>;
}
```

**Rules:**
- One CSS file per component, same name, in `frontend/src/styles/components/`.
- Class names use `kebab-case`, scoped by component prefix (e.g. `.agent-card`, `.agent-card__title`, `.agent-card--active`) to avoid collisions since there's no CSS Modules scoping.
- No inline `style={}` except for values that are genuinely dynamic and can't be a class (e.g. a computed chart width). Colors, spacing, fonts, and radius are never inlined.

## Design tokens (`variables.css`)

All tokens are defined once in `frontend/src/styles/variables.css` as CSS custom properties on `:root`, and referenced everywhere via `var(--token-name)`.

```css
/* frontend/src/styles/variables.css */

:root {
  /* Backgrounds */
  --bg-primary: #1e1f22;
  --bg-secondary: #2a2b2f;
  --bg-tertiary: #333438;

  /* Text */
  --text-primary: #e4e4e7;
  --text-secondary: #9c9ca3;
  --text-disabled: #5a5a60;

  /* Accent */
  --accent: #7c93c4;
  --accent-hover: #8fa4d1;

  /* Status (muted, used only for indicators — never large fills) */
  --status-success: #7fb58a;
  --status-warning: #d9b26f;
  --status-error: #c97b7b;
  --status-info: #7c93c4;

  /* Borders */
  --border: #3a3b40;

  /* Typography */
  --font-family: -apple-system, "SF Pro Text", "Segoe UI", sans-serif;
  --font-family-mono: "SF Mono", "Menlo", monospace;
  --font-size-h1: 22px;
  --font-size-h2: 16px;
  --font-size-body: 13px;
  --font-size-caption: 11px;

  /* Spacing scale */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Corner radius */
  --radius-sm: 6px;   /* badges, chips */
  --radius-md: 10px;  /* buttons, inputs */
  --radius-lg: 14px;  /* cards, panels */

  /* Motion */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
}
```

**Rules:**
- Any new color, spacing value, or radius must be added here first — never a raw hex/px value in a component CSS file.
- Status colors (`--status-*`) are reserved for status dots/badges/borders only, never backgrounds of large areas.
- Don't introduce a third font size mid-scale — stick to the four defined sizes.

## Typography

- Use `var(--font-family)` for all UI text, `var(--font-family-mono)` for anything numeric/log-like (agent IDs, log output, metrics, timestamps in logs).
- Max two font sizes per screen/card.
- Prefer whitespace (`--space-*`) over tight line-height to create visual breathing room.

```css
.agent-card__title {
  font-family: var(--font-family);
  font-size: var(--font-size-h2);
  font-weight: 600;
  color: var(--text-primary);
}

.agent-card__timestamp {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-caption);
  color: var(--text-secondary);
}
```

## Corners and shape

Every card, button, input, and panel is rounded — no sharp 0-radius corners anywhere, including nested elements inside cards.

```css
.agent-card {
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  padding: var(--space-md);
}

.button {
  border-radius: var(--radius-md);
}

.badge {
  border-radius: var(--radius-sm);
}
```

## Icons

- Use **[Lucide](https://lucide.dev/) icons** via the `lucide-react` package — single consistent icon set project-wide, don't mix icon libraries.
- Outline style only, single color (`var(--text-secondary)` by default, `var(--accent)` when active) — never filled/solid, never multi-color.
- Standard sizes: `16` (inline with text), `20` (buttons), `24` (sidebar/nav).
- Every icon must have an adjacent text label or `title`/`aria-label` — never icon-only controls.

```jsx
import { Play } from "lucide-react";

<button className="button button--primary">
  <Play size={20} color="var(--text-secondary)" />
  Start Agent
</button>
```

## Motion and transitions

Motion should confirm an action happened, never decorate. Keep it fast (150–250ms) using the `--transition-fast` / `--transition-base` tokens. Only animate `color`, `background-color`, `border-color`, `opacity`, and `transform` — never animate layout properties like `width`/`height`/`top`/`left` (causes jank).

**Hover state (apply to every interactive element):**

```css
.button {
  background: var(--bg-tertiary);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.button:hover {
  background: var(--accent-hover);
  color: var(--bg-primary);
}
```

**Fade-in for new elements appearing** (e.g. a new agent card mounting):

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

.agent-card {
  animation: fade-in var(--transition-base);
}
```

**Status change flash** (e.g. agent goes idle → running):

```css
.status-dot {
  transition: background-color var(--transition-base);
}
```

Then update the dot's color via a state-driven class change (`status-dot--success`, `status-dot--error`, etc.) rather than inline style, so the CSS transition animates it automatically.

**Rules:**
- Every interactive element (buttons, sidebar items, cards) needs a `:hover` and `:focus-visible` state.
- Never exceed 300ms for any transition — slower reads as laggy, not smooth.
- Respect reduced motion: wrap non-essential animations (like `fade-in`) in a media query.

```css
@media (prefers-reduced-motion: reduce) {
  .agent-card {
    animation: none;
  }
}
```

## Layout and intuitiveness rules

- **One primary action per screen**, visually distinct via `var(--accent)` background. All other actions use muted/secondary button styling.
- **Sidebar for navigation, page content for everything else.** Don't introduce new top-level nav patterns (tabs, dropdown menus) without strong reason — extend `Sidebar.jsx`.
- **Status is always visible via dot + text label**, never color alone (accessibility — don't rely on color perception).
- **Empty states are designed, not blank.** Any list/panel with no data shows a muted icon + short instructional text (e.g. "No agents yet — add one to get started"), not empty whitespace.
- **Consistent card anatomy** across all card-style components: status indicator → title → metadata (muted, small, mono if numeric) → actions (right-aligned). Don't invent a new layout per card type.
- **Loading states are explicit.** While `usePolling` is fetching initial data, show a skeleton/muted placeholder — never a blank screen or layout shift when data arrives.

## Component checklist

Before adding a new component to `frontend/src/components/` or `frontend/src/pages/`, confirm it:

- [ ] Has its own CSS file in `frontend/src/styles/components/`, imported directly
- [ ] Uses only `var(--...)` tokens from `variables.css` — no raw hex, px, or font values
- [ ] Uses `lucide-react` icons only, with a visible label or `aria-label`
- [ ] Has `:hover` and `:focus-visible` states if interactive
- [ ] Uses `border-radius` from the token scale on every rounded element
- [ ] Handles empty state and loading state if it renders list/async data
- [ ] Fetches data only if it's a `pages/` component — `components/` receive data via props