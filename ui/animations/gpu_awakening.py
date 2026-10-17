"""
gpu_awakening.py — GPU "Soul Awakening" Transition Orchestrator
================================================================
When the user toggles GPU ON, this module orchestrates:
  1. Brief white flash across the window
  2. Accent color transition (indigo → cyan)
  3. Panel borders start glowing
  4. Particle system ramps up
  5. Heartbeat indicator begins
  6. Status text announces awakening
When toggled OFF, a calm reverse transition plays.
"""

import tkinter as tk
from theme import ANIM, GPU_OVERLAY


class GPUAwakening:
    """Orchestrates the full GPU on/off visual transition."""

    def __init__(self, root: tk.Tk, canvas: tk.Canvas,
                 particle_system, glow_engine, status_callback):
        self.root = root
        self.canvas = canvas
        self.particles = particle_system
        self.glow = glow_engine
        self.status_cb = status_callback   # fn(text) -> update status label

    def awaken(self):
        """Play the GPU-ON awakening sequence."""
        # Step 1: flash
        self._flash(on=True)

        # Step 2: after flash, ramp up systems
        self.root.after(ANIM["awakening_flash"] + 50, self._activate)

    def calm(self):
        """Play the GPU-OFF calm-down sequence."""
        self._flash(on=False)
        self.root.after(ANIM["awakening_flash"] + 50, self._deactivate)

    # ── internal ───────────────────────────────────────────────────
    def _flash(self, on=True):
        """Brief bright overlay on canvas."""
        w = max(self.canvas.winfo_width(), 800)
        h = max(self.canvas.winfo_height(), 800)
        color = GPU_OVERLAY["flash_color"] if on else "#0f172a"
        flash_id = self.canvas.create_rectangle(
            0, 0, w, h,
            fill=color, outline="", tags="flash", stipple="gray50"
        )
        self.canvas.tag_raise("flash")
        # fade out
        self.root.after(
            ANIM["awakening_flash"],
            lambda: self.canvas.delete("flash")
        )

    def _activate(self):
        self.particles.set_gpu_mode(True)
        if not self.particles._running:
            self.particles.start(gpu_mode=True)
        self.glow.set_gpu_mode(True)
        self.status_cb("⚡ GPU Mode Activated — UI Alive!")

    def _deactivate(self):
        self.particles.set_gpu_mode(False)
        self.glow.set_gpu_mode(False)
        self.status_cb("CPU Mode — Standby")
