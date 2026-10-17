"""
effects.py — GPU Glow, Logo Color Cycle, Pulsating Dot
=======================================================
"""

import math
import tkinter as tk
import theme as T


class GlowEngine:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._running = False
        self._gpu = False
        self._panels: list[tk.Widget] = []
        self._gpu_dot = None
        self._logo_label = None
        self._logo_colors = [T.PURPLE, T.CYAN, T.GREEN, T.AMBER]
        self._logo_idx = 0
        self._pulse_phase = 0.0
        self._aids: list = []

    def register_panel(self, w):
        self._panels.append(w)

    def register_logo(self, lbl):
        self._logo_label = lbl

    def register_gpu_dot(self, canvas):
        self._gpu_dot = canvas

    def start(self):
        self._running = True
        self._cycle_logo()

    def stop(self):
        self._running = False
        for a in self._aids:
            try:
                self.root.after_cancel(a)
            except Exception:
                pass
        self._aids.clear()

    def set_gpu(self, on: bool):
        self._gpu = on
        if on:
            self._pulse_dot()

    def _cycle_logo(self):
        if not self._running:
            return
        if self._logo_label and self._gpu:
            self._logo_idx = (self._logo_idx + 1) % len(self._logo_colors)
            try:
                self._logo_label.config(fg=self._logo_colors[self._logo_idx])
            except Exception:
                pass
        a = self.root.after(T.ANIM["logo_tick"], self._cycle_logo)
        self._aids.append(a)

    def _pulse_dot(self):
        if not self._running or not self._gpu:
            return
        self._pulse_phase += 0.1
        t = (math.sin(self._pulse_phase * 2) + 1) / 2
        r = 3 + int(t * 4)
        if self._gpu_dot:
            try:
                self._gpu_dot.coords("dot", 8 - r, 8 - r, 8 + r, 8 + r)
                self._gpu_dot.itemconfig("dot", fill=T.GREEN)
            except Exception:
                pass
        a = self.root.after(T.ANIM["pulse_tick"], self._pulse_dot)
        self._aids.append(a)
