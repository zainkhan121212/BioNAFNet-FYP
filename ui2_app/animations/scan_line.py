"""
scan_line.py — Horizontal Scan Line
=====================================
Cyan sweep line moves top-to-bottom.
"""

import tkinter as tk
import theme as T


class ScanLine:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self._running = False
        self._aid = None
        self._y = -5
        self._line_id = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._y = -5
        self._line_id = self.canvas.create_line(
            0, self._y, 2000, self._y,
            fill=T.PURPLE_GLOW, width=2, tags="scanline",
            stipple="gray50"
        )
        self.canvas.tag_raise("scanline")
        self._tick()

    def stop(self):
        self._running = False
        if self._aid:
            self.canvas.after_cancel(self._aid)
        self.canvas.delete("scanline")
        self._line_id = None

    def _tick(self):
        if not self._running or not self._line_id:
            return
        h = max(self.canvas.winfo_height(), 800)
        self._y += 2
        if self._y > h + 10:
            self._y = -5
        try:
            self.canvas.coords(self._line_id, 0, self._y, 2000, self._y)
        except tk.TclError:
            pass
        self._aid = self.canvas.after(T.ANIM["scan_tick"], self._tick)
