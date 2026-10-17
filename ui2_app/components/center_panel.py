"""
center_panel.py — Neumorphic Image Viewer
===========================================
Soft shadow toolbar, inset canvas viewport, zoom/rotate controls.
"""

import tkinter as tk
from PIL import Image, ImageTk
import theme as T
from neumorphic import neu_card, neu_inset, hover_glow


class CenterPanel:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=T.BG)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.current_photo = None
        self.zoom = 100
        self.rotation = 0
        self._build()

    def _build(self):
        # ── TOOLBAR (neumorphic bar) ──────────────────────────────
        tb_outer, tb_surface = neu_card(self.frame, fill=tk.X)
        self.toolbar_outer = tb_outer
        toolbar = tk.Frame(tb_surface, bg=T.BG, height=40)
        toolbar.pack(fill=tk.X, padx=8, pady=6)
        toolbar.pack_propagate(False)
        self.toolbar = toolbar

        # Zoom controls
        zf = tk.Frame(toolbar, bg=T.BG)
        zf.pack(side=tk.LEFT, padx=4)

        self.zoom_out = self._soft_btn(zf, "🔍−", lambda: self._change_zoom(-25))
        self.zoom_out.pack(side=tk.LEFT, padx=2)

        self.zoom_lbl = tk.Label(zf, text="100%", font=T.FONT_MONO,
                                  bg=T.INSET_BG, fg=T.TEXT2, padx=10, pady=3)
        self.zoom_lbl.pack(side=tk.LEFT, padx=4)

        self.zoom_in = self._soft_btn(zf, "🔍+", lambda: self._change_zoom(25))
        self.zoom_in.pack(side=tk.LEFT, padx=2)

        # Separator
        tk.Frame(zf, width=2, height=20, bg=T.BG_LIGHT).pack(side=tk.LEFT, padx=8)

        self.rotate_btn = self._soft_btn(zf, "↺", self._rotate)
        self.rotate_btn.pack(side=tk.LEFT, padx=2)

        self.fit_btn = self._soft_btn(zf, "⊡", self._reset_view)
        self.fit_btn.pack(side=tk.LEFT, padx=2)

        # Compare button (right side)
        self.compare_btn = tk.Label(
            toolbar, text="⇄  Compare", font=T.FONT_SMALL,
            bg=T.BG, fg=T.TEXT3, cursor="hand2", padx=12, pady=4
        )
        self.compare_btn.pack(side=tk.RIGHT, padx=6)
        self.compare_btn.bind("<Button-1>", lambda e: self.app.toggle_comparison())
        hover_glow(self.compare_btn, T.BG, T.BG_LIGHT, T.TEXT3, T.PURPLE)

        # ── VIEWPORT (inset neumorphic canvas) ────────────────────
        vp_outer, vp_surface = neu_inset(self.frame, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.viewport_outer = vp_outer

        self.canvas = tk.Canvas(vp_surface, bg=T.INSET_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)
        self._draw_placeholder()

    def _soft_btn(self, parent, text, cmd):
        btn = tk.Label(parent, text=text, font=T.FONT_SMALL,
                        bg=T.BG, fg=T.TEXT2, cursor="hand2", padx=8, pady=3)
        btn.bind("<Button-1>", lambda e: cmd())
        hover_glow(btn, T.BG, T.BG_LIGHT, T.TEXT2, T.TEXT)
        return btn

    def _change_zoom(self, delta):
        self.zoom = max(25, min(400, self.zoom + delta))
        self.zoom_lbl.config(text=f"{self.zoom}%")
        self._update_display()

    def _rotate(self):
        self.rotation = (self.rotation - 90) % 360
        self._update_display()

    def _reset_view(self):
        self.zoom = 100
        self.rotation = 0
        self.zoom_lbl.config(text="100%")
        self._update_display()

    def _on_resize(self, e=None):
        self._draw_grid()

    def _draw_grid(self):
        self.canvas.delete("grid")
        if self.app.gpu_enabled.get():
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            for xi in range(0, w, 35):
                self.canvas.create_line(xi, 0, xi, h, fill="#1a1b2a", tags="grid")
            for yi in range(0, h, 35):
                self.canvas.create_line(0, yi, w, yi, fill="#1a1b2a", tags="grid")
        self.canvas.tag_lower("grid")

    def _draw_placeholder(self):
        self.canvas.delete("placeholder")
        self.canvas.create_text(
            400, 250,
            text="🖼️\n\nNo Image Selected\nUpload and select an image to begin",
            font=("Segoe UI", 14), fill=T.TEXT_HINT, justify=tk.CENTER,
            tags="placeholder"
        )

    def show_placeholder(self):
        self.canvas.delete("img")
        cx = max(self.canvas.winfo_width() // 2, 400)
        cy = max(self.canvas.winfo_height() // 2, 250)
        self.canvas.delete("placeholder")
        self.canvas.create_text(
            cx, cy,
            text="🖼️\n\nNo Image Selected\nUpload and select an image to begin",
            font=("Segoe UI", 14), fill=T.TEXT_HINT, justify=tk.CENTER,
            tags="placeholder"
        )

    def show_image(self, pil_img, idx, total, filename):
        self.canvas.delete("placeholder")
        self.canvas.delete("img")
        self.canvas.delete("overlay")
        cw = max(self.canvas.winfo_width() - 40, 200)
        ch = max(self.canvas.winfo_height() - 40, 200)

        scaled_w = int(pil_img.width * self.zoom / 100)
        scaled_h = int(pil_img.height * self.zoom / 100)
        img = pil_img.resize((min(scaled_w, cw), min(scaled_h, ch)),
                              Image.Resampling.LANCZOS)
        if self.rotation:
            img = img.rotate(-self.rotation, expand=True)

        self.current_photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(
            cw // 2 + 20, ch // 2 + 20,
            image=self.current_photo, anchor=tk.CENTER, tags="img"
        )
        self.canvas.create_text(
            30, ch + 10, text=filename, font=T.FONT_TINY,
            fill=T.TEXT2, anchor=tk.SW, tags="overlay"
        )

    def _update_display(self):
        self.app._update_display()

    def apply_theme(self):
        gpu = self.app.gpu_enabled.get()
        self._draw_grid()
        self.compare_btn.config(fg=T.PURPLE if gpu else T.TEXT3)
