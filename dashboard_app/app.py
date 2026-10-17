"""
app.py — Dark Neumorphism Dashboard Layout
============================================
Assembles Login Card, Line Chart, Donut Chart, and Quick Actions
into a single scrollable canvas window.
"""

import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import theme as T
from login_card import draw_login_card
from charts import draw_line_chart, draw_donut_chart
from quick_actions import draw_quick_actions
from neumorphic import neumorphic_card, rounded_rect


class NeuDashboard:
    CANVAS_W = 1350
    CANVAS_H = 820

    def __init__(self, root):
        self.root = root
        root.title("Dark Neumorphism Dashboard")
        root.geometry(f"{self.CANVAS_W}x{self.CANVAS_H}")
        root.config(bg=T.BG)
        root.resizable(True, True)

        # try dark title bar
        try:
            import pywinstyles
            pywinstyles.apply_style(root, "dark")
        except Exception:
            pass

        self.canvas = tk.Canvas(root, bg=T.BG, highlightthickness=0,
                                 width=self.CANVAS_W, height=self.CANVAS_H)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._draw()

    def _draw(self):
        c = self.canvas

        # ── Header ─────────────────────────────────────────────────
        c.create_text(40, 35, text="⬢  NeuBoard", font=T.FONT_TITLE,
                      fill=T.TEXT_PRIMARY, anchor=tk.W)
        c.create_text(40, 62, text="Dark Neumorphism Dashboard",
                      font=T.FONT_SMALL, fill=T.TEXT_SECONDARY, anchor=tk.W)

        # purple accent line under header
        c.create_line(40, 80, 300, 80, fill=T.PURPLE, width=3)
        c.create_line(300, 80, 350, 80, fill=T.PURPLE_DIM, width=3)

        # Notification & avatar area (top-right)
        self._draw_top_right(c)

        # ── Stat cards row ─────────────────────────────────────────
        stats = [
            ("$48,295", "Total Revenue",  "↑ 12.5%", T.PURPLE),
            ("2,847",   "Active Users",   "↑ 8.3%",  T.GREEN),
            ("1,249",   "New Orders",     "↑ 5.7%",  T.ORANGE),
            ("98.5%",   "Uptime",         "↑ 0.2%",  T.CYAN),
        ]
        stat_w, stat_h = 270, 110
        stat_gap = 30
        sx = 40
        sy = 100
        for val, label, change, accent in stats:
            neumorphic_card(c, sx, sy, stat_w, stat_h)
            # Accent dot
            c.create_oval(sx + 22, sy + 22, sx + 30, sy + 30,
                          fill=accent, outline="")
            c.create_text(sx + 38, sy + 26, text=label, font=T.FONT_SMALL,
                          fill=T.TEXT_SECONDARY, anchor=tk.W)
            c.create_text(sx + 22, sy + 60, text=val, font=T.FONT_BIG_NUM,
                          fill=T.TEXT_PRIMARY, anchor=tk.W)
            c.create_text(sx + stat_w - 22, sy + stat_h - 22, text=change,
                          font=T.FONT_TINY, fill=accent, anchor=tk.E)
            sx += stat_w + stat_gap

        # ── Row 2: Line Chart + Donut Chart ───────────────────────
        row2_y = 235
        draw_line_chart(c, 40, row2_y, w=680, h=310)
        draw_donut_chart(c, 755, row2_y, w=310, h=310)

        # ── Row 3: Login Card + Quick Actions ──────────────────────
        row3_y = 570
        draw_login_card(c, 40, row3_y, w=380, h=230)

        # Quick Actions on right
        draw_quick_actions(c, 455, row3_y, w=610, h=140)

        # Extra: Recent Activity mini-card
        self._draw_activity(c, 455, row3_y + 165, 610, 65)

    def _draw_top_right(self, c):
        # Search input
        rx = self.CANVAS_W - 360
        neumorphic_card(c, rx, 25, 200, 40, r=20, inset=True)
        c.create_text(rx + 16, 45, text="🔍  Search...", font=T.FONT_SMALL,
                      fill=T.TEXT_HINT, anchor=tk.W)

        # Notification bell
        bx = self.CANVAS_W - 130
        rounded_rect(c, bx, 28, bx + 36, 64, 12, fill=T.BG_LIGHT, outline="")
        c.create_text(bx + 18, 46, text="🔔", font=("Segoe UI Emoji", 14))
        # red dot
        c.create_oval(bx + 24, 28, bx + 34, 38, fill=T.RED, outline=T.BG, width=2)
        c.create_text(bx + 29, 33, text="3", font=(T.FONT_FAMILY, 7, "bold"),
                      fill="white")

        # Avatar
        ax = self.CANVAS_W - 70
        c.create_oval(ax, 28, ax + 36, 64, fill=T.PURPLE_DIM, outline=T.BG_LIGHT, width=2)
        c.create_text(ax + 18, 46, text="G", font=(T.FONT_FAMILY, 14, "bold"),
                      fill="white")

    def _draw_activity(self, c, x, y, w, h):
        neumorphic_card(c, x, y, w, h)
        c.create_text(x + 20, y + 18, text="📊  Recent Activity",
                      font=T.FONT_SMALL, fill=T.TEXT_PRIMARY, anchor=tk.W)
        c.create_text(x + 20, y + 40, text="3 new transactions • 2 pending approvals • System healthy",
                      font=T.FONT_TINY, fill=T.TEXT_SECONDARY, anchor=tk.W)
        # green dot
        c.create_oval(x + w - 30, y + 25, x + w - 18, y + 37,
                      fill=T.GREEN, outline="")
