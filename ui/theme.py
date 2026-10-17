"""
theme.py — Premium Color Palettes, Fonts & Glassmorphism Config
================================================================
Rich, vibrant dark-first design with neon accents.
"""

# ── Fonts ──────────────────────────────────────────────────────────
FONT_FAMILY       = "Segoe UI"
FONT_TITLE        = (FONT_FAMILY, 24, "bold")
FONT_HEADING      = (FONT_FAMILY, 13, "bold")
FONT_SUBHEADING   = (FONT_FAMILY, 12, "bold")
FONT_BODY         = (FONT_FAMILY, 11)
FONT_SMALL        = (FONT_FAMILY, 10)
FONT_TINY         = (FONT_FAMILY, 9)
FONT_BUTTON       = (FONT_FAMILY, 12, "bold")
FONT_BUTTON_SM    = (FONT_FAMILY, 11)
FONT_LOGO         = (FONT_FAMILY, 30, "bold")
FONT_ENHANCE_BTN  = (FONT_FAMILY, 16, "bold")

# ── Glass Panel Config ─────────────────────────────────────────────
GLASS_BORDER_W    = 2
GLASS_GLOW_W      = 3

# ── Dark Theme (DEFAULT — dramatic, premium look) ─────────────────
DARK = {
    "name":             "superhero",
    # backgrounds — deep space gradient feel
    "bg":               "#080c18",         # near-black deep blue
    "bg_alt":           "#0d1224",         # slightly lighter
    "sidebar":          "#111827",         # dark slate
    "card":             "#151d30",         # card surface
    "canvas_bg":        "#060a14",         # deepest, for image viewer

    # accents — indigo/violet neon
    "accent":           "#7c3aed",         # violet-600
    "accent_hover":     "#6d28d9",         # violet-700
    "accent_light":     "#a78bfa",         # violet-400
    "accent_subtle":    "#1e1147",         # deep violet background

    # text
    "text":             "#f1f5f9",
    "text_secondary":   "#94a3b8",
    "text_muted":       "#64748b",

    # borders — glowing
    "border":           "#1e293b",
    "border_accent":    "#4c1d95",         # violet-900 glow

    # status
    "success":          "#10b981",
    "success_hover":    "#059669",
    "warning":          "#f59e0b",
    "danger":           "#ef4444",

    # GPU
    "gpu_glow":         "#22d3ee",
    "gpu_bg":           "#0891b2",
    "gpu_particle":     "#67e8f9",

    # buttons
    "btn_bg":           "#1e293b",
    "btn_fg":           "#e2e8f0",
    "btn_hover_bg":     "#334155",

    # model card
    "model_selected":   "#7c3aed",
    "model_default_bg": "#1a2040",
    "model_default_fg": "#94a3b8",

    # frosted glass panels
    "glass_bg":         "#111827",
    "glass_border":     "#2d1b69",         # violet-tinted border
    "glass_highlight":  "#a78bfa",         # top-edge highlight

    # header gradient
    "header_bg":        "#0f1729",
    "header_border":    "#2d1b69",
}

# ── Light Theme ────────────────────────────────────────────────────
LIGHT = {
    "name":             "cosmo",
    "bg":               "#f0f2f8",
    "bg_alt":           "#e8ebf5",
    "sidebar":          "#ffffff",
    "card":             "#ffffff",
    "canvas_bg":        "#1a1a2e",

    "accent":           "#7c3aed",
    "accent_hover":     "#6d28d9",
    "accent_light":     "#c4b5fd",
    "accent_subtle":    "#ede9fe",

    "text":             "#1e293b",
    "text_secondary":   "#64748b",
    "text_muted":       "#94a3b8",

    "border":           "#e2e8f0",
    "border_accent":    "#c4b5fd",

    "success":          "#10b981",
    "success_hover":    "#059669",
    "warning":          "#f59e0b",
    "danger":           "#ef4444",

    "gpu_glow":         "#06b6d4",
    "gpu_bg":           "#0891b2",
    "gpu_particle":     "#22d3ee",

    "btn_bg":           "#e4e2ef",
    "btn_fg":           "#1e293b",
    "btn_hover_bg":     "#d0cde6",

    "model_selected":   "#7c3aed",
    "model_default_bg": "#f5f3ff",
    "model_default_fg": "#4c1d95",

    "glass_bg":         "#ffffffee",
    "glass_border":     "#c4b5fd",
    "glass_highlight":  "#a78bfa",

    "header_bg":        "#f8f7ff",
    "header_border":    "#c4b5fd",
}

# ── GPU "Alive" Overlay ───────────────────────────────────────────
GPU_OVERLAY = {
    "accent":           "#22d3ee",        # cyan-400
    "accent_hover":     "#06b6d4",        # cyan-500
    "accent_secondary": "#e879f9",        # fuchsia-400
    "glow_border":      "#22d3ee",
    "particle_primary": "#22d3ee",
    "particle_secondary": "#a78bfa",      # violet-400
    "particle_tertiary": "#f472b6",       # pink-400
    "heartbeat_color":  "#22d3ee",
    "flash_color":      "#ffffff",
    "model_selected":   "#22d3ee",
    "glass_border":     "#0e7490",
    "glass_highlight":  "#22d3ee",
}

# ── Animation Timings (ms) ────────────────────────────────────────
ANIM = {
    "particle_tick":       33,
    "glow_tick":           50,
    "color_cycle_tick":    80,
    "heartbeat_tick":      40,
    "logo_cycle_tick":     1000,
    "awakening_flash":     120,
    "awakening_transition":400,
    "hover_fade":          8,
}

# ── Particle Config ───────────────────────────────────────────────
PARTICLES = {
    "count_normal":    25,
    "count_gpu":       65,
    "size_min":        2,
    "size_max":        6,
    "speed_min":       0.2,
    "speed_max":       1.0,
    "connection_dist": 140,
}

# ── Logo Color Cycle ──────────────────────────────────────────────
LOGO_COLORS = [
    "#7c3aed",  # violet
    "#8b5cf6",  # violet-500
    "#a855f7",  # purple
    "#c084fc",  # purple-300
    "#d946ef",  # fuchsia
    "#a855f7",  # purple
    "#7c3aed",  # violet (loop)
]

GPU_LOGO_COLORS = [
    "#22d3ee",  # cyan
    "#06b6d4",  # cyan-dark
    "#a78bfa",  # violet
    "#e879f9",  # fuchsia
    "#f472b6",  # pink
    "#22d3ee",  # cyan (loop)
]


def get_theme(dark_mode: bool) -> dict:
    """Return the active color dict."""
    return DARK if dark_mode else LIGHT
