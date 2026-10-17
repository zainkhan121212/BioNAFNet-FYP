"""
theme.py — Futuristic Dark Theme Constants
=============================================
"""

# ── Colors ─────────────────────────────────────────────
BG_DARK       = "#0a0b14"    # deepest background
BG_MAIN       = "#0f1120"    # main content bg
BG_CARD       = "#151728"    # card / panel
BG_SIDEBAR    = "#0c0d1a"    # sidebar bg
BG_INPUT      = "#1a1c30"    # input fields
BG_HOVER      = "#1e2040"    # hover state

ACCENT        = "#00d4ff"    # neon cyan (primary)
ACCENT_DIM    = "#0099bb"    # dimmed cyan
ACCENT_PURPLE = "#8a2be2"    # neon purple (secondary)
ACCENT_GREEN  = "#00ff88"    # success green
ACCENT_ORANGE = "#ff8c42"    # warning orange
ACCENT_RED    = "#ff3b5c"    # danger red
ACCENT_GOLD   = "#ffd700"    # gold

TEXT          = "#ffffff"
TEXT_DIM      = "#8b8fa8"
TEXT_MUTED    = "#4a4e6a"
TEXT_DARK     = "#2a2e45"

BORDER        = "#1e2040"
BORDER_GLOW   = "#00d4ff"

# ── Fonts ──────────────────────────────────────────────
FONT_FAMILY   = "Segoe UI"
FONT_TITLE    = (FONT_FAMILY, 28, "bold")
FONT_HEADING  = (FONT_FAMILY, 16, "bold")
FONT_SUB      = (FONT_FAMILY, 13, "bold")
FONT_BODY     = (FONT_FAMILY, 12)
FONT_SMALL    = (FONT_FAMILY, 11)
FONT_TINY     = (FONT_FAMILY, 10)
FONT_MONO     = ("Consolas", 11)
FONT_ICON     = ("Segoe UI Emoji", 16)
FONT_ICON_LG  = ("Segoe UI Emoji", 22)
FONT_NAV      = (FONT_FAMILY, 13)
FONT_NAV_BOLD = (FONT_FAMILY, 13, "bold")

# ── Models ─────────────────────────────────────────────
MODELS = [
    {"id": "zero_dce",      "name": "Zero-DCE",      "icon": "⚡", "desc": "Zero-Reference Deep Curve Estimation"},
    {"id": "mirnet",        "name": "MIRNet",         "icon": "🧠", "desc": "Multi-Scale Residual Block Network"},
    {"id": "enlightengan",  "name": "EnlightenGAN",   "icon": "✨", "desc": "Unsupervised GAN Enhancement"},
    {"id": "retinexnet",    "name": "RetinexNet",     "icon": "🔆", "desc": "Retinex-based Deep Enhancer"},
    {"id": "kind",          "name": "KinD",           "icon": "💎", "desc": "Kindling the Darkness"},
]

# ── Sidebar Pages ──────────────────────────────────────
PAGES = [
    {"key": "enhance",      "label": "Enhance",       "icon": "✦"},
    {"key": "augmentation", "label": "Augmentation",   "icon": "🔀"},
    {"key": "resizing",     "label": "Resizing",       "icon": "📐"},
    {"key": "cropping",     "label": "Cropping",       "icon": "✂"},
    {"key": "live_preview", "label": "Live Preview",   "icon": "📡"},
]
