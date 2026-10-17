"""
theme.py — Dark Neumorphism Color Palette & Constants
======================================================
Deep matte blue-gray with neon purple accents.
"""

# ── Surface ────────────────────────────────────────────
BG           = "#1e1f2b"     # Main background & card surface
BG_DARK      = "#181924"     # Dark shadow
BG_LIGHT     = "#272838"     # Light shadow

# For "inset" elements (inputs)
INSET_BG     = "#191a25"
INSET_DARK   = "#131420"
INSET_LIGHT  = "#242535"

# ── Accent ─────────────────────────────────────────────
PURPLE       = "#8a2be2"     # Primary neon purple
PURPLE_GLOW  = "#a855f7"     # Lighter purple for glow
PURPLE_DIM   = "#6d22b3"     # Darker purple
ORANGE       = "#ff8c42"     # Data viz accent 1
GREEN        = "#2ecc71"     # Data viz accent 2
CYAN         = "#00d4ff"
RED          = "#ef4444"

# ── Text ───────────────────────────────────────────────
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#6c6e82"
TEXT_MUTED     = "#44465a"
TEXT_HINT      = "#393b50"

# ── Neumorphic Settings ───────────────────────────────
SHADOW_OFFSET  = 6          # px offset for shadows
SHADOW_BLUR    = 12         # approx blur (layers)
CORNER_RADIUS  = 22         # rounded corner radius
CARD_PAD       = 28         # inner padding

# ── Fonts ──────────────────────────────────────────────
FONT_FAMILY      = "Segoe UI"
FONT_TITLE       = (FONT_FAMILY, 26, "bold")
FONT_HEADING     = (FONT_FAMILY, 16, "bold")
FONT_SUBHEADING  = (FONT_FAMILY, 13, "bold")
FONT_BODY        = (FONT_FAMILY, 12)
FONT_SMALL       = (FONT_FAMILY, 11)
FONT_TINY        = (FONT_FAMILY, 10)
FONT_MONO        = ("Consolas", 11)
FONT_BUTTON      = (FONT_FAMILY, 14, "bold")
FONT_BIG_NUM     = (FONT_FAMILY, 32, "bold")
FONT_ICON        = ("Segoe UI Emoji", 18)
