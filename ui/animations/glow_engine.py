"""
glow_engine.py — Pulsing Glow, Border Breathing & Color Cycling
=================================================================
Visual effects that make the UI feel alive.
"""

import math
import tkinter as tk
from theme import ANIM, LOGO_COLORS, GPU_LOGO_COLORS, GPU_OVERLAY


class GlowEngine:
    """Drives pulsating glows, color cycling, and hover effects."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._running = False
        self._gpu_mode = False
        self._tick_count = 0

        # widgets to animate
        self._logo_label = None
        self._gpu_indicator = None
        self._glow_panels: list[tk.Widget] = []
        self._glow_buttons: list[tk.Widget] = []

        # state
        self._logo_idx = 0
        self._pulse_phase = 0.0
        self._heartbeat_phase = 0.0

        self._after_ids: list[str] = []

    # ── registration ───────────────────────────────────────────────
    def register_logo(self, label: tk.Label):
        self._logo_label = label

    def register_gpu_indicator(self, canvas: tk.Canvas):
        self._gpu_indicator = canvas

    def register_glow_panel(self, widget: tk.Widget):
        self._glow_panels.append(widget)

    def register_glow_button(self, widget: tk.Widget):
        self._glow_buttons.append(widget)

    # ── public API ─────────────────────────────────────────────────
    def start(self):
        self._running = True
        self._cycle_logo()

    def stop(self):
        self._running = False
        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def set_gpu_mode(self, enabled: bool):
        self._gpu_mode = enabled
        if enabled:
            self._start_gpu_effects()
        else:
            self._stop_gpu_effects()

    # ── logo color cycle ───────────────────────────────────────────
    def _cycle_logo(self):
        if not self._running:
            return
        colors = GPU_LOGO_COLORS if self._gpu_mode else LOGO_COLORS
        self._logo_idx = (self._logo_idx + 1) % len(colors)
        if self._logo_label:
            try:
                self._logo_label.config(fg=colors[self._logo_idx])
            except tk.TclError:
                pass
        aid = self.root.after(ANIM["logo_cycle_tick"], self._cycle_logo)
        self._after_ids.append(aid)

    # ── GPU-mode effects ───────────────────────────────────────────
    def _start_gpu_effects(self):
        self._pulse_glow()
        self._heartbeat()

    def _stop_gpu_effects(self):
        # reset panel borders to normal theme
        from theme import get_theme
        t = get_theme(True)  # use dark theme defaults
        for panel in self._glow_panels:
            try:
                panel.config(highlightbackground=t["glass_border"],
                             highlightthickness=2)
            except (tk.TclError, AttributeError):
                pass

    def _pulse_glow(self):
        """Smoothly pulsate panel border color between base and glow."""
        if not self._running or not self._gpu_mode:
            return
        self._pulse_phase += 0.08
        # oscillate 0..1
        t = (math.sin(self._pulse_phase) + 1) / 2
        glow = GPU_OVERLAY["glow_border"]

        # interpolate highlight thickness 1 → 3
        thickness = 1 + int(t * 2)
        for panel in self._glow_panels:
            try:
                panel.config(
                    highlightbackground=glow,
                    highlightthickness=thickness
                )
            except (tk.TclError, AttributeError):
                pass

        aid = self.root.after(ANIM["glow_tick"], self._pulse_glow)
        self._after_ids.append(aid)

    def _heartbeat(self):
        """Pulsate the GPU indicator dot like a heartbeat."""
        if not self._running or not self._gpu_mode:
            return
        self._heartbeat_phase += 0.12
        t = (math.sin(self._heartbeat_phase) + 1) / 2
        # scale dot size between 6 and 14
        radius = 6 + int(t * 8)
        cx, cy = 8, 8
        if self._gpu_indicator:
            try:
                self._gpu_indicator.coords(
                    "indicator",
                    cx - radius // 2, cy - radius // 2,
                    cx + radius // 2, cy + radius // 2,
                )
                col = GPU_OVERLAY["heartbeat_color"]
                self._gpu_indicator.itemconfig("indicator", fill=col)
            except tk.TclError:
                pass

        aid = self.root.after(ANIM["heartbeat_tick"], self._heartbeat)
        self._after_ids.append(aid)


def add_hover_glow(widget: tk.Widget, normal_bg: str, hover_bg: str,
                   normal_fg: str = None, hover_fg: str = None):
    """Attach enter/leave hover color swap to a widget."""
    def on_enter(e):
        try:
            widget.config(bg=hover_bg)
            if hover_fg:
                widget.config(fg=hover_fg)
        except tk.TclError:
            pass

    def on_leave(e):
        try:
            widget.config(bg=normal_bg)
            if normal_fg:
                widget.config(fg=normal_fg)
        except tk.TclError:
            pass

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
