"""
quick_actions.py — Square Rounded Quick-Action Buttons
=======================================================
Send, Receive, Swap, History — in a neumorphic card.
"""

import tkinter as tk
import theme as T
from neumorphic import neumorphic_card, rounded_rect


def draw_quick_actions(canvas, x, y, w=520, h=140):
    """Draw a row of 4 quick-action buttons inside a neumorphic card."""
    neumorphic_card(canvas, x, y, w, h)

    canvas.create_text(x + 25, y + 22, text="Quick Actions",
                       font=T.FONT_SUBHEADING, fill=T.TEXT_PRIMARY, anchor=tk.W)

    actions = [
        ("📤", "Send",    T.PURPLE),
        ("📥", "Receive", T.GREEN),
        ("🔄", "Swap",    T.ORANGE),
        ("📋", "History", T.CYAN),
    ]

    btn_size = 70
    gap = (w - 50 - len(actions) * btn_size) // (len(actions) - 1)
    start_x = x + 25
    btn_y = y + 50

    for i, (icon, label, accent) in enumerate(actions):
        bx = start_x + i * (btn_size + gap)

        # Neumorphic shadow for each button
        off = 4
        r = 18
        # dark shadow
        rounded_rect(canvas, bx + off, btn_y + off,
                     bx + btn_size + off, btn_y + btn_size + off, r,
                     fill=T.BG_DARK, outline="")
        # light shadow
        rounded_rect(canvas, bx - off // 2, btn_y - off // 2,
                     bx + btn_size - off // 2, btn_y + btn_size - off // 2, r,
                     fill=T.BG_LIGHT, outline="")
        # surface
        rounded_rect(canvas, bx, btn_y, bx + btn_size, btn_y + btn_size, r,
                     fill=T.BG, outline="")

        # Icon with accent color
        cx = bx + btn_size // 2
        cy = btn_y + btn_size // 2 - 6
        canvas.create_text(cx, cy, text=icon, font=("Segoe UI Emoji", 20),
                           fill=accent)

        # Label below
        canvas.create_text(cx, btn_y + btn_size + 14, text=label,
                           font=T.FONT_TINY, fill=T.TEXT_SECONDARY)
