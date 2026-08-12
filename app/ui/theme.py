COLORS = {
    # Backgrounds
    "bg_primary": "#1E1F22",
    "bg_secondary": "#2A2B2F",
    "bg_tertiary": "#333438",

    # Text
    "text_primary": "#E4E4E7",
    "text_secondary": "#9C9CA3",
    "text_disabled": "#5A5A60",
    "button_fg": "#FFFFFF",

    # Accent
    "accent": "#7C93C4",
    "accent_hover": "#8FA4D1",

    # Status colors
    "success": "#7FB58A",
    "warning": "#D9B26F",
    "error": "#C97B7B",
    "info": "#7C93C4",

    # Borders / dividers
    "border": "#3A3B40",

    # Code / message surfaces
    "code_bg": "#23252b",
    "code_fg": "#E4E4E7",
    "user_bg": "#272A31",
    "assistant_bg": "#23252b",
    "system_bg": "#26292f",
}

FONTS = {
    "family": "SF Pro Text",
    "family_mono": "SF Mono",
    "size_h1": 22,
    "size_h2": 16,
    "size_body": 13,
    "size_caption": 11,
    "weight_bold": "bold",
    "weight_normal": "normal",
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

CORNER_RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 14,
}

THEMES = {
    "light": {
        **COLORS,
        "bg_primary": "#F4F6FB",
        "bg_secondary": "#FFFFFF",
        "bg_tertiary": "#F1F3F7",
        "text_primary": "#101828",
        "text_secondary": "#6B7280",
        "text_disabled": "#9CA3AF",
        "accent": "#4F46E5",
        "accent_hover": "#4338CA",
        "code_bg": "#F3F4F6",
        "code_fg": "#111827",
        "user_bg": "#EEF2FF",
        "assistant_bg": "#FFFFFF",
        "system_bg": "#F8FAFC",
    },
    "dark": {
        **COLORS,
    },
    "hacker": {
        "bg_primary": "#020602",
        "bg_secondary": "#061708",
        "bg_tertiary": "#081a08",
        "text_primary": "#9BFF9B",
        "text_secondary": "#6DA56D",
        "text_disabled": "#395D39",
        "accent": "#23FF00",
        "accent_hover": "#55FF55",
        "success": "#7FB58A",
        "warning": "#D9B26F",
        "error": "#C97B7B",
        "info": "#23FF00",
        "border": "#14400f",
        "code_bg": "#071908",
        "code_fg": "#8CFF8C",
        "user_bg": "#081108",
        "assistant_bg": "#061008",
        "system_bg": "#041006",
    },
}
