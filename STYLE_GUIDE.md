# UI Style Guide: parallax

Defines the visual and interaction standards for the parallax dashboard. Read this before writing or editing any file in `app/ui/`. All values here should be sourced from `app/ui/theme.py` — never hardcoded inline in widget files.

## Design direction

Clean, modern, minimal. Muted color palette, generous whitespace, rounded corners, minimal iconography, subtle motion. The UI should never feel cluttered or require explanation — every screen should be understandable in a few seconds.

## Library choice: use `customtkinter`, not raw `tkinter`

Raw `tkinter` cannot produce rounded corners, modern color rendering, or built-in dark mode — it will fight against every goal in this guide. Use **`customtkinter`** (`pip install customtkinter`) for all new UI code. It wraps tkinter with rounded widgets, native-feeling theming, and dark/light mode support out of the box.

```python
import customtkinter as ctk

ctk.set_appearance_mode("dark")       # "dark", "light", or "system"
ctk.set_default_color_theme("blue")   # overridden by theme.py values below
```

Only fall back to raw `tkinter` widgets for things customtkinter doesn't provide (e.g. embedding matplotlib in `metrics_chart.py`), and style them to match as closely as possible.

## Color palette

Muted, low-saturation palette. Defined once in `app/ui/theme.py`, imported everywhere else.

```python
# app/ui/theme.py

COLORS = {
    # Backgrounds
    "bg_primary":     "#1E1F22",   # main window background (dark mode)
    "bg_secondary":    "#2A2B2F",   # cards, panels
    "bg_tertiary":    "#333438",   # hover/pressed surfaces

    # Text
    "text_primary":   "#E4E4E7",   # headings, primary content
    "text_secondary": "#9C9CA3",   # captions, timestamps, muted labels
    "text_disabled":  "#5A5A60",

    # Accent (muted, not saturated)
    "accent":         "#7C93C4",   # primary actions, active states
    "accent_hover":   "#8FA4D1",

    # Status colors (muted, not neon)
    "success":        "#7FB58A",   # agent running
    "warning":        "#D9B26F",   # agent idle/waiting
    "error":          "#C97B7B",   # agent failed/error
    "info":           "#7C93C4",

    # Borders / dividers
    "border":         "#3A3B40",
}
```

**Rules:**
- Never use pure black (`#000000`) or pure white (`#FFFFFF`) — always use the muted values above.
- Status colors (`success`/`warning`/`error`) are used **only** for agent state indicators (dots, badges, borders) — never as large fill areas.
- Every new color must be added to `COLORS` in `theme.py` before use. No inline hex codes in widget files.

## Typography

```python
# app/ui/theme.py

FONTS = {
    "family": "SF Pro Text",   # falls back to system default on non-macOS
    "family_mono": "SF Mono",  # for logs, IDs, code-like content

    "size_h1": 22,   # window/section titles
    "size_h2": 16,   # card titles
    "size_body": 13, # default body text
    "size_caption": 11,  # timestamps, secondary labels

    "weight_bold": "bold",
    "weight_normal": "normal",
}
```

**Rules:**
- Use `FONTS["family_mono"]` for anything numeric/log-like (agent IDs, log output, metrics) — improves scannability.
- Max two font sizes per screen/card. Don't introduce new sizes outside this scale.
- Line height: allow generous padding around text blocks (see Spacing) rather than tight line spacing.

## Spacing scale

Use a consistent spacing scale everywhere — no arbitrary pixel values in widget code.

```python
# app/ui/theme.py

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}
```

Apply via `padx`/`pady`, e.g. `pady=SPACING["md"]`. Cards and panels should default to `SPACING["md"]` internal padding; sections should be separated by `SPACING["lg"]`.

## Corners and shape

- All cards, buttons, input fields, and panels use rounded corners. In customtkinter, set `corner_radius` explicitly — don't rely on defaults, so it stays consistent project-wide.

```python
CORNER_RADIUS = {
    "sm": 6,    # small elements: badges, chips
    "md": 10,   # buttons, inputs
    "lg": 14,   # cards, panels
}
```

```python
card = ctk.CTkFrame(
    parent,
    corner_radius=CORNER_RADIUS["lg"],
    fg_color=COLORS["bg_secondary"],
    border_width=1,
    border_color=COLORS["border"],
)
```

- No sharp 0-radius corners anywhere in the UI, including nested elements within cards.

## Icons

- Use a single, consistent minimalist icon set — do not mix icon styles. Recommended: [Feather Icons](https://feathericons.com/) or [Lucide](https://lucide.dev/) rendered as PNG/SVG-to-PNG assets, stored in `assets/icons/`.
- Icons are **outline style**, single-color (tinted to `COLORS["text_secondary"]` by default, `COLORS["accent"]` when active), never filled/solid, never multi-color.
- Standard icon sizes: `16px` (inline with text), `20px` (buttons), `24px` (sidebar/nav).
- Every icon must have a text label or tooltip nearby — never icon-only controls, to preserve intuitiveness.

```python
icon_label = ctk.CTkLabel(
    parent,
    image=load_icon("play", size=20, color=COLORS["text_secondary"]),
    text="Start Agent",
    compound="left",
    font=(FONTS["family"], FONTS["size_body"]),
)
```

## Motion and transitions

Raw tkinter/customtkinter has no built-in animation system — transitions must be hand-rolled with `root.after()` loops. Keep all motion **subtle and fast** (150–250ms). Motion should confirm an action occurred, never decorate.

**Standard fade-in helper** (use for cards/panels appearing, e.g. a new agent card being added):

```python
# app/ui/widgets/_animation.py

def fade_in(widget, duration_ms=200, steps=10):
    """Fade a widget in by animating its foreground color alpha via step-wise
    color interpolation. customtkinter widgets don't support true alpha,
    so this interpolates from bg color to target color instead."""
    interval = duration_ms // steps

    def step(i=0):
        if i > steps:
            return
        # Interpolate opacity via color blend as a stand-in for alpha
        widget.configure(fg_color=_blend(
            COLORS["bg_primary"], widget._target_color, i / steps
        ))
        widget.after(interval, lambda: step(i + 1))

    step()
```

**Standard hover transition** (apply to all clickable elements — buttons, cards, sidebar items):

```python
def bind_hover(widget, base_color, hover_color):
    widget.bind("<Enter>", lambda e: widget.configure(fg_color=hover_color))
    widget.bind("<Leave>", lambda e: widget.configure(fg_color=base_color))
```

**Rules:**
- Every interactive element (buttons, sidebar items, agent cards) must have a hover state using `bind_hover`.
- Status changes (agent goes from idle → running) should briefly flash the status color, not snap instantly — use a short `fade_in`-style transition.
- Never use motion longer than 300ms — anything slower feels laggy, not smooth.
- Avoid animating layout/position (expensive, janky in tkinter). Only animate color/opacity.

## Layout and intuitiveness rules

- **One primary action per screen.** The most important button (e.g. "New Agent", "Start All") should be visually distinct (accent color); everything else is secondary/muted.
- **Sidebar for navigation, main panel for content** — don't introduce new top-level navigation patterns (tabs, menus) without strong reason; keep to the sidebar model defined in `app/ui/widgets/sidebar.py`.
- **Status is always visible at a glance.** Every agent card must show a colored status dot (`success`/`warning`/`error`) plus a text label — never color alone (accessibility).
- **Empty states are designed, not blank.** Any list/panel with no data (e.g. no agents yet) shows a muted icon + short instructional text, not an empty white space.
- **Consistent card anatomy.** Every card-style widget (agent card, log entry, etc.) follows: icon/status → title → metadata (muted, small) → actions (right-aligned). Don't invent new card layouts per widget.

## Component checklist

Before adding a new widget to `app/ui/widgets/`, confirm it:

- [ ] Uses `customtkinter`, not raw `tkinter`, unless embedding a non-customtkinter element (e.g. matplotlib)
- [ ] Pulls all colors from `COLORS` in `theme.py`
- [ ] Pulls all fonts from `FONTS` in `theme.py`
- [ ] Pulls all spacing from `SPACING` in `theme.py`
- [ ] Uses `CORNER_RADIUS` values, never a raw radius number
- [ ] Has a hover state if interactive (`bind_hover`)
- [ ] Has an icon + label if it represents an action (never icon-only)
- [ ] Handles its own empty/loading state if it displays a list or async data