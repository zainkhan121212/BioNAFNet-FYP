"""
right_panel.py — Neumorphic Collapsible Tool Sections
=======================================================
Resize, Crop, Augmentation, Advanced — extruded cards with inset toggles.
"""

import tkinter as tk
import theme as T
from neumorphic import neu_card, neu_inset, neu_entry, hover_glow


class CollapsibleSection:
    """A neumorphic collapsible card with optional toggle switch."""

    ACCENT_MAP = {
        "cyan":    T.CYAN,
        "purple":  T.PURPLE,
        "emerald": T.GREEN,
        "amber":   T.AMBER,
    }

    def __init__(self, parent, title, icon, app, accent="cyan",
                 has_toggle=True, default_on=False, default_expanded=False):
        self.app = app
        self.enabled = default_on
        self.expanded = default_expanded
        self.accent = accent
        self.accent_color = self.ACCENT_MAP.get(accent, T.CYAN)

        # Neumorphic outer card
        self.outer, self.surface = neu_card(parent, fill=tk.X, pady=4)

        # Header row
        hdr = tk.Frame(self.surface, bg=T.BG, cursor="hand2")
        hdr.pack(fill=tk.X, padx=14, pady=10)
        self._hdr = hdr
        hdr.bind("<Button-1>", lambda e: self.toggle_expand())

        # Accent dot
        self.dot = tk.Canvas(hdr, width=10, height=10, bg=T.BG,
                              highlightthickness=0)
        self.dot.pack(side=tk.LEFT, padx=(0, 6))
        self.dot.create_oval(1, 1, 9, 9, fill=self.accent_color, outline="")

        tk.Label(hdr, text=icon, font=("Segoe UI", 11), bg=T.BG,
                 fg=T.TEXT3).pack(side=tk.LEFT)
        self.title_lbl = tk.Label(hdr, text=f"  {title}", font=T.FONT_HEADING,
                                   bg=T.BG, fg=T.TEXT)
        self.title_lbl.pack(side=tk.LEFT)
        self.title_lbl.bind("<Button-1>", lambda e: self.toggle_expand())

        self.chevron = tk.Label(hdr, text="▸", font=("Segoe UI", 12),
                                 bg=T.BG, fg=T.TEXT3)
        self.chevron.pack(side=tk.RIGHT, padx=4)
        self.chevron.bind("<Button-1>", lambda e: self.toggle_expand())

        # Toggle switch (inset neumorphic)
        if has_toggle:
            self.toggle_canvas = tk.Canvas(hdr, width=40, height=20,
                                            bg=T.BG, highlightthickness=0,
                                            cursor="hand2")
            self.toggle_canvas.pack(side=tk.RIGHT, padx=6)
            self._draw_toggle()
            self.toggle_canvas.bind("<Button-1>", lambda e: self._toggle_switch())

        # Content area
        self.content = tk.Frame(self.surface, bg=T.BG)
        if default_expanded:
            self.content.pack(fill=tk.X, padx=14, pady=(0, 10))
            self.chevron.config(text="▾")

    def toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.content.pack(fill=tk.X, padx=14, pady=(0, 10))
            self.chevron.config(text="▾")
        else:
            self.content.pack_forget()
            self.chevron.config(text="▸")

    def _toggle_switch(self):
        self.enabled = not self.enabled
        self._draw_toggle()

    def _draw_toggle(self):
        c = self.toggle_canvas
        c.delete("all")
        # Inset track
        c.create_rectangle(0, 3, 40, 17, fill=T.INSET_BG, outline=T.INSET_DARK, width=1)
        if self.enabled:
            # Accent fill
            c.create_rectangle(2, 4, 38, 16, fill=self.accent_color, outline="")
            # White knob (right)
            c.create_oval(24, 2, 38, 18, fill=T.TEXT, outline="")
        else:
            c.create_rectangle(2, 4, 38, 16, fill=T.INSET_BG, outline="")
            # Gray knob (left)
            c.create_oval(2, 2, 16, 18, fill=T.TEXT3, outline="")

    def apply_theme(self):
        gpu = self.app.gpu_enabled.get()
        self.outer.set_glow(gpu and self.enabled, self.accent_color)
        if hasattr(self, "toggle_canvas"):
            self._draw_toggle()


class RightPanel:
    WIDTH = 280

    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=T.BG, width=self.WIDTH)
        self.frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame.pack_propagate(False)
        self._build()

    def _build(self):
        inner = tk.Frame(self.frame, bg=T.BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._inner = inner

        # Title
        thdr = tk.Frame(inner, bg=T.BG)
        thdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(thdr, text="⚙️", font=("Segoe UI", 12), bg=T.BG,
                 fg=T.PURPLE).pack(side=tk.LEFT)
        self.panel_title = tk.Label(thdr, text="  Processing Tools", font=T.FONT_HEADING,
                                     bg=T.BG, fg=T.TEXT)
        self.panel_title.pack(side=tk.LEFT)

        # ── Resize ──────────────────────────────────────────────
        self.resize_sec = CollapsibleSection(
            inner, "Resizing", "📐", self.app, "cyan", True, True, True
        )
        rc = self.resize_sec.content

        dim_row = tk.Frame(rc, bg=T.BG)
        dim_row.pack(fill=tk.X, pady=4)
        wf = tk.Frame(dim_row, bg=T.BG)
        wf.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(wf, text="Width (px)", font=T.FONT_TINY, bg=T.BG,
                 fg=T.TEXT3).pack(anchor=tk.W)
        w_outer, self.w_entry = neu_entry(wf, width=7)
        w_outer.pack(fill=tk.X)
        self.w_entry.insert(0, "1920")

        tk.Label(dim_row, text="🔗", font=("Segoe UI", 10), bg=T.BG,
                 fg=T.TEXT3).pack(side=tk.LEFT, padx=4, pady=10)

        hf = tk.Frame(dim_row, bg=T.BG)
        hf.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(hf, text="Height (px)", font=T.FONT_TINY, bg=T.BG,
                 fg=T.TEXT3).pack(anchor=tk.W)
        h_outer, self.h_entry = neu_entry(hf, width=7)
        h_outer.pack(fill=tk.X)
        self.h_entry.insert(0, "1080")

        # Presets
        prow = tk.Frame(rc, bg=T.BG)
        prow.pack(fill=tk.X, pady=4)
        for label, w, h in [("HD", 1280, 720), ("FHD", 1920, 1080), ("4K", 3840, 2160)]:
            btn = tk.Label(prow, text=label, font=T.FONT_TINY,
                            bg=T.BG, fg=T.TEXT2, cursor="hand2", padx=12, pady=5)
            btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            btn.bind("<Button-1>", lambda e, ww=w, hh=h: self._set_dims(ww, hh))
            hover_glow(btn, T.BG, T.BG_LIGHT, T.TEXT2, T.TEXT)

        # ── Crop ─────────────────────────────────────────────
        self.crop_sec = CollapsibleSection(
            inner, "Cropping", "✂️", self.app, "purple", True, False, False
        )
        cc = self.crop_sec.content
        rrow = tk.Frame(cc, bg=T.BG)
        rrow.pack(fill=tk.X, pady=4)
        for ratio in ["1:1", "4:3", "16:9", "3:2", "9:16", "Free"]:
            btn = tk.Label(rrow, text=ratio, font=T.FONT_TINY,
                            bg=T.BG, fg=T.TEXT2, cursor="hand2", padx=6, pady=4)
            btn.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
            hover_glow(btn, T.BG, T.BG_LIGHT, T.TEXT2, T.TEXT)

        frow = tk.Frame(cc, bg=T.BG)
        frow.pack(fill=tk.X, pady=4)
        for lbl in ["H-Flip", "V-Flip", "Rotate"]:
            btn = tk.Label(frow, text=lbl, font=T.FONT_TINY,
                            bg=T.BG, fg=T.TEXT2, cursor="hand2", padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            hover_glow(btn, T.BG, T.BG_LIGHT, T.TEXT2, T.TEXT)

        # ── Augmentation ──────────────────────────────────────
        self.aug_sec = CollapsibleSection(
            inner, "Data Augmentation", "🔀", self.app, "emerald", True, False, False
        )
        ac = self.aug_sec.content
        augs = [("Random Rotation", "±15°"), ("Horizontal Flip", "50%"),
                ("Vertical Flip", "50%"), ("Color Jitter", "B,C"),
                ("Random Crop", "80-100%"), ("Gaussian Noise", "σ=0.01")]
        for name, sub in augs:
            arow = tk.Frame(ac, bg=T.BG)
            arow.pack(fill=tk.X, pady=1)
            tk.Label(arow, text=name, font=T.FONT_TINY, bg=T.BG,
                     fg=T.TEXT2, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(arow, text=sub, font=T.FONT_TINY, bg=T.BG,
                     fg=T.TEXT_HINT).pack(side=tk.RIGHT)

        # ── Advanced ──────────────────────────────────────────
        self.adv_sec = CollapsibleSection(
            inner, "Advanced", "🎚️", self.app, "amber", False, False, False
        )
        adc = self.adv_sec.content
        for lbl in ["Brightness", "Contrast", "Saturation", "Sharpness"]:
            sf = tk.Frame(adc, bg=T.BG)
            sf.pack(fill=tk.X, pady=2)
            tk.Label(sf, text=lbl, font=T.FONT_TINY, bg=T.BG,
                     fg=T.TEXT2).pack(side=tk.LEFT)
            tk.Label(sf, text="0", font=T.FONT_TINY, bg=T.BG,
                     fg=T.TEXT_HINT).pack(side=tk.RIGHT)

        self.sections = [self.resize_sec, self.crop_sec, self.aug_sec, self.adv_sec]

    def _set_dims(self, w, h):
        self.w_entry.delete(0, tk.END)
        self.w_entry.insert(0, str(w))
        self.h_entry.delete(0, tk.END)
        self.h_entry.insert(0, str(h))

    def apply_theme(self):
        for sec in self.sections:
            sec.apply_theme()
