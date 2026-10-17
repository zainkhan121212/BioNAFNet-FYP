"""
neumorphic.py — Soft UI True Canvas Rendering for Tkinter
===========================================================
Replaces harsh tf.Frame borders with beautifully blended, rounded
Canvas polygons for a genuine "squircle" neumorphic extrude.
"""

import tkinter as tk
import theme as T


def blend(c1, c2, t):
    """Linearly blend hex color c1 to c2 by factor t (0.0=c1, 1.0=c2)."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def create_poly(x1, y1, x2, y2, r):
    """Return a point sequence for a rounded rectangle."""
    return [
        x1+r, y1,  x2-r, y1,  x2, y1,  x2, y1+r,
        x2, y2-r,  x2, y2,  x2-r, y2,  x1+r, y2,
        x1, y2,  x1, y2-r,  x1, y1+r,  x1, y1
    ]


class NeuWidget(tk.Frame):
    """A container that draws its own soft shadow background."""
    def __init__(self, parent, style="outset", **kwargs):
        super().__init__(parent, bg=T.BG, **kwargs)
        self.style = style
        self.canvas = tk.Canvas(self, bg=T.BG, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.surface_bg = T.INSET_BG if style == "inset" else T.BG
        self.content = tk.Frame(self, bg=self.surface_bg)
        
        # Padding bounds
        self.pad_box = 18 if style == "outset" else 8
        self.content_pad = self.pad_box + (10 if style == "outset" else 6)
        
        self.content.pack(fill=tk.BOTH, expand=True,
                          padx=self.content_pad, pady=self.content_pad)
        
        self.bind("<Configure>", self._redraw)
        self._glow = False
        self._glow_color = T.PURPLE
        self._drawn_w = 0
        self._drawn_h = 0
        
    def set_glow(self, state, color=T.PURPLE):
        self._glow = state
        self._glow_color = color
        self._redraw(force=True)
        
    def _redraw(self, event=None, force=False):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20 or h < 20: return
        if not force and w == self._drawn_w and h == self._drawn_h: return
        self._drawn_w, self._drawn_h = w, h
        
        c = self.canvas
        c.delete("all")
        
        r = T.NEU_RADIUS
        bx1, by1 = self.pad_box, self.pad_box
        bx2, by2 = w - self.pad_box, h - self.pad_box
        
        if self.style == "outset":
            steps = 8
            off = T.NEU_OFFSET + 2
            # Dark shadow (bottom-right)
            for i in range(steps):
                t = i / steps
                col = blend(T.BG_DARK, T.BG, t)
                dist = off * (1 - t)
                poly = create_poly(bx1+dist, by1+dist, bx2+dist, by2+dist, r)
                c.create_polygon(poly, smooth=True, fill=col, outline="")
                
            # Light shadow (top-left)
            for i in range(steps):
                t = i / steps
                col = blend(T.BG_LIGHT, T.BG, t)
                dist = off * (1 - t)
                poly = create_poly(bx1-dist, by1-dist, bx2-dist, by2-dist, r)
                c.create_polygon(poly, smooth=True, fill=col, outline="")
                
            # Glow Outline
            if self._glow:
                for i in range(4):
                    t = i / 4
                    col = blend(self._glow_color, T.BG, t + 0.4)
                    dist = 4 * (1 - t)
                    poly = create_poly(bx1-dist, by1-dist, bx2+dist, by2+dist, r)
                    c.create_polygon(poly, smooth=True, outline=col, width=2)
                    
            # Surface
            c.create_polygon(create_poly(bx1, by1, bx2, by2, r), smooth=True, fill=self.surface_bg, outline="")
            
        elif self.style == "inset":
            # Outer surface
            c.create_polygon(create_poly(bx1, by1, bx2, by2, r), smooth=True, fill=self.surface_bg, outline="")
            # Inner shadows via stroked outlines offset
            c.create_polygon(create_poly(bx1, by1, bx2, by2, r), smooth=True, outline=T.INSET_DARK, width=3)
            c.create_polygon(create_poly(bx1-2, by1-2, bx2-2, by2-2, r), smooth=True, outline=T.BG_LIGHT, width=2)
            
            if self._glow:
                c.create_polygon(create_poly(bx1, by1, bx2, by2, r), smooth=True, outline=self._glow_color, width=2)


def neu_card(parent, **pack_kw):
    w = NeuWidget(parent, style="outset")
    if pack_kw: w.pack(**pack_kw)
    return w, w.content


def neu_inset(parent, **pack_kw):
    w = NeuWidget(parent, style="inset")
    if pack_kw: w.pack(**pack_kw)
    return w, w.content


def neu_button(parent, text, command=None, accent=False, icon=None, pill=False):
    """A button that acts exactly like NeuWidget but handles clicks."""
    w = NeuWidget(parent, style="outset")
    
    display = f"{icon}  {text}" if icon else text
    lbl = tk.Label(w.content, text=display, font=T.FONT_BUTTON if accent else T.FONT_BUTTON_SM,
                   bg=w.surface_bg, fg=T.TEXT if accent else T.TEXT2, cursor="hand2")
    lbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
    
    if accent:
        w.set_glow(True, T.PURPLE)
        lbl.config(fg=T.TEXT)
        def on_enter(e): w.set_glow(True, T.PURPLE_GLOW)
        def on_leave(e): w.set_glow(True, T.PURPLE)
    else:
        def on_enter(e): lbl.config(fg=T.TEXT)
        def on_leave(e): lbl.config(fg=T.TEXT2)
    
    lbl.bind("<Enter>", on_enter)
    lbl.bind("<Leave>", on_leave)
    
    if command:
        w.bind("<Button-1>", lambda e: command())
        lbl.bind("<Button-1>", lambda e: command())
        w.canvas.bind("<Button-1>", lambda e: command())
        
    return w


def neu_entry(parent, placeholder="", width=20):
    outer, surface = neu_inset(parent)
    entry = tk.Entry(surface, font=T.FONT_BODY, bg=T.INSET_BG, fg=T.TEXT,
                     insertbackground=T.PURPLE, bd=0, highlightthickness=0, width=width)
    entry.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    return outer, entry


def hover_glow(widget, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
    def enter(e):
        try:
            widget.config(bg=hover_bg)
            if hover_fg: widget.config(fg=hover_fg)
        except: pass
    def leave(e):
        try:
            widget.config(bg=normal_bg)
            if normal_fg: widget.config(fg=normal_fg)
        except: pass
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)
