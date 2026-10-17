"""
center_panel.py — Image Viewer with Glowing Border Card
=========================================================
"""

import os
import tkinter as tk
from PIL import Image, ImageTk
from theme import (
    FONT_SUBHEADING, FONT_BODY, FONT_SMALL, FONT_BUTTON_SM,
    get_theme, GPU_OVERLAY, GLASS_BORDER_W,
)
from animations.glow_engine import add_hover_glow


class CenterPanel:
    def __init__(self, parent: tk.Frame, app):
        self.app = app
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=6)

        self.current_photo = None
        self._build()

    def _build(self):
        t = get_theme(self.app.dark_mode.get())
        self.frame.config(bg=t["bg"])

        # viewer card with glass border
        self.viewer = tk.Frame(
            self.frame, bg=t["card"],
            highlightbackground=t["glass_border"],
            highlightthickness=GLASS_BORDER_W
        )
        self.viewer.pack(fill=tk.BOTH, expand=True)

        # top highlight
        self.top_line = tk.Frame(self.viewer, height=2, bg=t["glass_highlight"])
        self.top_line.pack(fill=tk.X)

        # header row
        hdr = tk.Frame(self.viewer, bg=t["card"], height=42)
        hdr.pack(fill=tk.X, padx=12, pady=6)
        hdr.pack_propagate(False)
        self._hdr = hdr

        self.view_title = tk.Label(
            hdr, text="🖼️  Image Preview & Comparison",
            font=FONT_SUBHEADING, bg=t["card"], fg=t["text"]
        )
        self.view_title.pack(side=tk.LEFT, pady=6)

        self.compare_var = tk.BooleanVar(value=False)
        self.compare_chk = tk.Checkbutton(
            hdr, text="  Side-by-side", variable=self.compare_var,
            font=FONT_SMALL, bg=t["card"], fg=t["text_secondary"],
            selectcolor=t["accent"], activebackground=t["card"],
            command=self.app.toggle_comparison
        )
        self.compare_chk.pack(side=tk.RIGHT, pady=6)

        # canvas for images
        self.canvas = tk.Canvas(
            self.viewer, bg=t["canvas_bg"], highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))

        # draw grid pattern on canvas for premium look
        self.canvas.bind("<Configure>", self._draw_grid)

        # placeholder text
        self._draw_placeholder(t)

        # nav bar
        nav = tk.Frame(self.viewer, bg=t["card"])
        nav.pack(fill=tk.X, padx=12, pady=(0, 10))
        self._nav = nav

        self.prev_btn = tk.Button(
            nav, text="◀  Previous", font=FONT_BUTTON_SM,
            bg=t["btn_bg"], fg=t["btn_fg"],
            activebackground=t["accent"], activeforeground="white",
            relief=tk.FLAT, padx=18, pady=8, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.prev_image
        )
        self.prev_btn.pack(side=tk.LEFT)
        add_hover_glow(self.prev_btn, t["btn_bg"], t["accent_subtle"],
                       t["btn_fg"], t["text"])

        self.info_label = tk.Label(
            nav, text="No image selected", font=FONT_BODY,
            bg=t["card"], fg=t["text_secondary"]
        )
        self.info_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = tk.Button(
            nav, text="Next  ▶", font=FONT_BUTTON_SM,
            bg=t["btn_bg"], fg=t["btn_fg"],
            activebackground=t["accent"], activeforeground="white",
            relief=tk.FLAT, padx=18, pady=8, cursor="hand2",
            bd=0, highlightthickness=0,
            command=self.app.next_image
        )
        self.next_btn.pack(side=tk.RIGHT)
        add_hover_glow(self.next_btn, t["btn_bg"], t["accent_subtle"],
                       t["btn_fg"], t["text"])

    def _draw_grid(self, event=None):
        """Subtle dot-grid pattern on canvas bg."""
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        t = get_theme(self.app.dark_mode.get())
        dot_color = "#1a2040" if self.app.dark_mode.get() else "#d0d5e3"
        spacing = 30
        for x in range(0, w, spacing):
            for y in range(0, h, spacing):
                self.canvas.create_oval(
                    x, y, x + 2, y + 2,
                    fill=dot_color, outline="", tags="grid"
                )
        # ensure grid is behind everything else
        self.canvas.tag_lower("grid")

    def _draw_placeholder(self, t):
        self.canvas.delete("placeholder")
        self.canvas.create_text(
            400, 260,
            text="📷  Upload images to begin\n\nSupports PNG · JPG · BMP · TIFF",
            font=("Segoe UI", 16), fill=t["text_muted"],
            justify=tk.CENTER, tags="placeholder"
        )

    def show_placeholder(self):
        self.canvas.delete("img")
        t = get_theme(self.app.dark_mode.get())
        self.canvas.delete("placeholder")
        cx = max(self.canvas.winfo_width() // 2, 400)
        cy = max(self.canvas.winfo_height() // 2, 260)
        self.canvas.create_text(
            cx, cy,
            text="📷  Upload images to begin\n\nSupports PNG · JPG · BMP · TIFF",
            font=("Segoe UI", 16), fill=t["text_muted"],
            justify=tk.CENTER, tags="placeholder"
        )
        self.info_label.config(text="No image selected")

    def show_image(self, pil_img, idx, total, filename):
        self.canvas.delete("placeholder")
        self.canvas.delete("img")
        cw = max(self.canvas.winfo_width() - 40, 200)
        ch = max(self.canvas.winfo_height() - 40, 200)
        pil_img.thumbnail((cw, ch), Image.Resampling.LANCZOS)
        self.current_photo = ImageTk.PhotoImage(pil_img)
        self.canvas.create_image(
            cw // 2 + 20, ch // 2 + 20,
            image=self.current_photo, anchor=tk.CENTER, tags="img"
        )
        short = filename if len(filename) <= 30 else filename[:27] + "..."
        self.info_label.config(text=f"{idx + 1}/{total}:  {short}")

    def apply_theme(self):
        t = get_theme(self.app.dark_mode.get())
        gpu = self.app.gpu_enabled.get()
        border = GPU_OVERLAY["glass_border"] if gpu else t["glass_border"]
        highlight = GPU_OVERLAY["glass_highlight"] if gpu else t["glass_highlight"]

        self.frame.config(bg=t["bg"])
        self.viewer.config(bg=t["card"], highlightbackground=border)
        self.top_line.config(bg=highlight)
        self._hdr.config(bg=t["card"])
        self.view_title.config(bg=t["card"], fg=t["text"])
        self.compare_chk.config(bg=t["card"], fg=t["text_secondary"],
                                selectcolor=t["accent"],
                                activebackground=t["card"])
        self.canvas.config(bg=t["canvas_bg"])
        self._draw_grid()
        self._nav.config(bg=t["card"])
        self.prev_btn.config(bg=t["btn_bg"], fg=t["btn_fg"])
        self.next_btn.config(bg=t["btn_bg"], fg=t["btn_fg"])
        self.info_label.config(bg=t["card"], fg=t["text_secondary"])
