"""
neumorphic.py — Canvas Drawing Primitives for Soft UI
======================================================
Rounded rectangles with dual drop-shadows for the "extruded" look.
"""

import tkinter as tk
import theme as T


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Draw a smooth rounded rectangle using polygon with smooth=True."""
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kw)


def neumorphic_card(canvas, x, y, w, h, r=None, inset=False):
    """Draw a full neumorphic card with dual shadows + surface.
    Returns the surface polygon ID.
    """
    if r is None:
        r = T.CORNER_RADIUS
    off = T.SHADOW_OFFSET

    if inset:
        # Inset neumorphism: dark shadow top-left, light shadow bottom-right
        rounded_rect(canvas, x - 2, y - 2, x + w, y + h, r,
                     fill=T.INSET_DARK, outline="")
        rounded_rect(canvas, x + 2, y + 2, x + w + 4, y + h + 4, r,
                     fill=T.INSET_LIGHT, outline="")
        surface = rounded_rect(canvas, x, y, x + w, y + h, r,
                               fill=T.INSET_BG, outline="")
    else:
        # Outset: light shadow top-left, dark shadow bottom-right
        # dark shadow (bottom-right)
        rounded_rect(canvas, x + off, y + off, x + w + off, y + h + off, r,
                     fill=T.BG_DARK, outline="")
        # light shadow (top-left)
        rounded_rect(canvas, x - off // 2, y - off // 2,
                     x + w - off // 2, y + h - off // 2, r,
                     fill=T.BG_LIGHT, outline="")
        # surface
        surface = rounded_rect(canvas, x, y, x + w, y + h, r,
                               fill=T.BG, outline="")
    return surface


def neumorphic_button(canvas, x, y, w, h, text, accent=False,
                      pill=False, icon=None, r=None):
    """Draw a neumorphic button. If accent=True, uses purple glow."""
    if r is None:
        r = h // 2 if pill else T.CORNER_RADIUS
    off = 4

    if accent:
        # Glow shadow behind
        rounded_rect(canvas, x - 2, y - 2, x + w + 2, y + h + 2, r,
                     fill=T.PURPLE_DIM, outline="")
        # Purple surface
        rounded_rect(canvas, x, y, x + w, y + h, r,
                     fill=T.PURPLE, outline="")
        fg = T.TEXT_PRIMARY
    else:
        # Standard neumorphic
        rounded_rect(canvas, x + off, y + off, x + w + off, y + h + off, r,
                     fill=T.BG_DARK, outline="")
        rounded_rect(canvas, x - off // 2, y - off // 2,
                     x + w - off // 2, y + h - off // 2, r,
                     fill=T.BG_LIGHT, outline="")
        rounded_rect(canvas, x, y, x + w, y + h, r,
                     fill=T.BG, outline="")
        fg = T.TEXT_SECONDARY

    cx, cy = x + w // 2, y + h // 2
    display = f"{icon}  {text}" if icon else text
    canvas.create_text(cx, cy, text=display, font=T.FONT_BUTTON if accent else T.FONT_BODY,
                       fill=fg, anchor=tk.CENTER)


def neumorphic_input(canvas, x, y, w, h, placeholder="", r=None):
    """Draw an inset neumorphic input field with placeholder text."""
    if r is None:
        r = h // 2
    neumorphic_card(canvas, x, y, w, h, r=r, inset=True)
    canvas.create_text(x + 18, y + h // 2, text=placeholder,
                       font=T.FONT_BODY, fill=T.TEXT_HINT, anchor=tk.W)
