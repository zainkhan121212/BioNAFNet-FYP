"""
theme.py — Dark Neumorphism (Soft UI) Design System
=====================================================
Deep matte blue-gray with dual soft shadows, neon purple accents.
"""

FONT_FAMILY    = "Segoe UI"
FONT_TITLE     = (FONT_FAMILY, 22, "bold")
FONT_HEADING   = (FONT_FAMILY, 13, "bold")
FONT_BODY      = (FONT_FAMILY, 11)
FONT_SMALL     = (FONT_FAMILY, 10)
FONT_TINY      = (FONT_FAMILY, 9)
FONT_MONO      = ("Consolas", 10)
FONT_MONO_SM   = ("Consolas", 9)
FONT_BUTTON    = (FONT_FAMILY, 13, "bold")
FONT_BUTTON_SM = (FONT_FAMILY, 11, "bold")
FONT_LOGO      = (FONT_FAMILY, 22, "bold")
FONT_ENHANCE   = (FONT_FAMILY, 14, "bold")

# ── Surface Colors ─────────────────────────────────────
BG           = "#1e1f2b"     # main background & card surface (same!)
BG_DARK      = "#161722"     # dark shadow (bottom-right)
BG_LIGHT     = "#272838"     # light shadow (top-left)
BG_DEEP      = "#14151f"     # slightly deeper for variety

# ── Inset (pressed-in) fields ──────────────────────────
INSET_BG     = "#181924"
INSET_DARK   = "#121320"
INSET_LIGHT  = "#242535"

# ── Accent: Neon Purple ────────────────────────────────
PURPLE       = "#8a2be2"     # primary accent
PURPLE_GLOW  = "#a855f7"     # lighter glow
PURPLE_DIM   = "#6d22b3"     # darker purple for shadow

# ── Secondary Accents ──────────────────────────────────
ORANGE       = "#ff8c42"
GREEN        = "#2ecc71"
CYAN         = "#00d4ff"
RED          = "#ef4444"
AMBER        = "#f59e0b"
BLUE         = "#3b82f6"

# ── Text ───────────────────────────────────────────────
TEXT         = "#ffffff"      # pure white headers
TEXT2        = "#8b8da3"      # muted blue-gray secondary
TEXT3        = "#595b72"      # faint labels / placeholders
TEXT_HINT    = "#3e4058"      # very faint

# ── Neumorphic Settings ───────────────────────────────
NEU_OFFSET   = 5             # shadow offset px
NEU_RADIUS   = 20            # corner radius (conceptual)

# ── Button Defaults ───────────────────────────────────
BTN_BG       = BG            # same as surface
BTN_FG       = TEXT2          # muted text
BTN_HOVER    = BG_LIGHT      # slightly lighter on hover

# ── GPU Colors ─────────────────────────────────────────
GPU = {
    "cyan":    CYAN,
    "purple":  PURPLE,
    "emerald": GREEN,
    "amber":   AMBER,
    "flash":   "#ffffff",
}

# ── Models ─────────────────────────────────────────────
MODELS = [
    {"id": "A", "name": "Zero-DCE",      "desc": "Zero-Reference Deep Curve Estimation",   "icon": "⚡"},
    {"id": "B", "name": "RetinexNet",     "desc": "Retinex-based Deep Enhancement",         "icon": "🔆"},
    {"id": "C", "name": "MIRNet",         "desc": "Multi-Scale Residual Block Network",     "icon": "🧠"},
    {"id": "D", "name": "EnlightenGAN",   "desc": "Unsupervised GAN Enhancement",           "icon": "✨"},
    {"id": "E", "name": "RUAS",           "desc": "Retinex-inspired Unrolling Architecture","icon": "🔄"},
    {"id": "F", "name": "SNR-Aware",      "desc": "Signal-to-Noise Ratio Aware Model",      "icon": "📊"},
    {"id": "G", "name": "SCI",            "desc": "Self-Calibrated Illumination Learning",  "icon": "💎"},
]

PARTICLE_COLORS = [CYAN, PURPLE, GREEN, AMBER]

ANIM = {
    "particle_tick":  33,
    "scan_tick":      16,
    "glow_tick":      50,
    "logo_tick":      1200,
    "pulse_tick":     40,
}
