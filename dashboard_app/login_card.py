"""
login_card.py — Neumorphic Login Card
=======================================
Email + password inputs with a purple "Sign Up" pill button.
"""

import tkinter as tk
import theme as T
from neumorphic import neumorphic_card, neumorphic_input, neumorphic_button, rounded_rect


def draw_login_card(canvas, x, y, w=380, h=420):
    """Draw a complete login card at (x, y)."""
    # Card
    neumorphic_card(canvas, x, y, w, h)

    # Title
    canvas.create_text(x + w // 2, y + 45, text="Welcome Back",
                       font=T.FONT_HEADING, fill=T.TEXT_PRIMARY)
    canvas.create_text(x + w // 2, y + 68, text="Sign in to your account",
                       font=T.FONT_SMALL, fill=T.TEXT_SECONDARY)

    # Avatar circle
    av_cx, av_cy, av_r = x + w // 2, y + 120, 30
    rounded_rect(canvas, av_cx - av_r - 4, av_cy - av_r - 4,
                 av_cx + av_r + 4, av_cy + av_r + 4, av_r + 4,
                 fill=T.BG_DARK, outline="")
    rounded_rect(canvas, av_cx - av_r, av_cy - av_r,
                 av_cx + av_r, av_cy + av_r, av_r,
                 fill=T.BG, outline="")
    canvas.create_text(av_cx, av_cy, text="👤", font=("Segoe UI Emoji", 22),
                       fill=T.TEXT_MUTED)

    # Email input
    neumorphic_input(canvas, x + 35, y + 170, w - 70, 48, placeholder="✉  Email address")

    # Password input
    neumorphic_input(canvas, x + 35, y + 235, w - 70, 48, placeholder="🔒  Password")

    # Forgot password
    canvas.create_text(x + w - 40, y + 298, text="Forgot password?",
                       font=T.FONT_TINY, fill=T.PURPLE, anchor=tk.E)

    # Sign Up button (pill, accent)
    btn_w, btn_h = w - 70, 50
    neumorphic_button(canvas, x + 35, y + 318, btn_w, btn_h,
                      text="Sign Up", accent=True, pill=True)

    # Divider
    div_y = y + 385
    canvas.create_line(x + 40, div_y, x + w // 2 - 20, div_y,
                       fill=T.TEXT_MUTED, width=1)
    canvas.create_text(x + w // 2, div_y, text="or", font=T.FONT_TINY,
                       fill=T.TEXT_MUTED)
    canvas.create_line(x + w // 2 + 20, div_y, x + w - 40, div_y,
                       fill=T.TEXT_MUTED, width=1)
