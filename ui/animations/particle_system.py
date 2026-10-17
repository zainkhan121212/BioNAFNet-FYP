"""
particle_system.py — Floating Constellation Particle Engine
=============================================================
Renders drifting dots on a Canvas with connection lines between
nearby particles (constellation effect).  Reacts to GPU mode.
"""

import random, math
import tkinter as tk
from theme import PARTICLES, ANIM, GPU_OVERLAY


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "size", "color", "oid")

    def __init__(self, x, y, vx, vy, size, color, oid=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.oid = oid          # canvas object id


class ParticleSystem:
    """Manages all floating particles on a background Canvas."""

    def __init__(self, canvas: tk.Canvas, get_theme_fn):
        self.canvas = canvas
        self.get_theme = get_theme_fn     # callable -> current theme dict
        self.particles: list[Particle] = []
        self._running = False
        self._gpu_mode = False
        self._after_id = None

    # ── public API ─────────────────────────────────────────────────
    def start(self, gpu_mode=False):
        self._gpu_mode = gpu_mode
        self._running = True
        self._spawn_particles()
        self._tick()

    def stop(self):
        self._running = False
        if self._after_id:
            self.canvas.after_cancel(self._after_id)
            self._after_id = None
        self.canvas.delete("particle")
        self.canvas.delete("pline")
        self.particles.clear()

    def set_gpu_mode(self, enabled: bool):
        was = self._gpu_mode
        self._gpu_mode = enabled
        if enabled and not was:
            # add more particles
            self._spawn_particles(extra=True)
        elif not enabled and was:
            # trim down
            self._trim_particles()

    # ── internals ──────────────────────────────────────────────────
    def _spawn_particles(self, extra=False):
        cfg = PARTICLES
        target = cfg["count_gpu"] if self._gpu_mode else cfg["count_normal"]
        if extra:
            target = cfg["count_gpu"]
        current = len(self.particles)
        to_add = max(0, target - current)

        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 400)

        colors = self._particle_colors()
        for _ in range(to_add):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            vx = random.uniform(-cfg["speed_max"], cfg["speed_max"])
            vy = random.uniform(-cfg["speed_max"], cfg["speed_max"])
            # ensure minimum speed
            if abs(vx) < cfg["speed_min"]:
                vx = cfg["speed_min"] * (1 if vx >= 0 else -1)
            if abs(vy) < cfg["speed_min"]:
                vy = cfg["speed_min"] * (1 if vy >= 0 else -1)
            sz = random.randint(cfg["size_min"], cfg["size_max"])
            col = random.choice(colors)

            oid = self.canvas.create_oval(
                x, y, x + sz, y + sz,
                fill=col, outline="", tags="particle"
            )
            self.particles.append(Particle(x, y, vx, vy, sz, col, oid))

    def _trim_particles(self):
        target = PARTICLES["count_normal"]
        while len(self.particles) > target:
            p = self.particles.pop()
            self.canvas.delete(p.oid)

    def _particle_colors(self):
        if self._gpu_mode:
            return [
                GPU_OVERLAY["particle_primary"],
                GPU_OVERLAY["particle_secondary"],
                GPU_OVERLAY["particle_tertiary"],
            ]
        theme = self.get_theme()
        return [theme["accent_light"], theme["accent"], theme["text_muted"]]

    def _tick(self):
        if not self._running:
            return

        w = max(self.canvas.winfo_width(), 400)
        h = max(self.canvas.winfo_height(), 400)

        # move particles
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            # bounce
            if p.x < 0 or p.x > w:
                p.vx *= -1
            if p.y < 0 or p.y > h:
                p.vy *= -1
            p.x = max(0, min(w, p.x))
            p.y = max(0, min(h, p.y))

            self.canvas.coords(p.oid, p.x, p.y, p.x + p.size, p.y + p.size)

        # draw connection lines (constellation effect)
        self.canvas.delete("pline")
        if self._gpu_mode:
            dist = PARTICLES["connection_dist"]
            theme = self.get_theme()
            line_col = theme.get("accent_light", "#c7d2fe")
            n = len(self.particles)
            for i in range(n):
                a = self.particles[i]
                for j in range(i + 1, n):
                    b = self.particles[j]
                    dx = a.x - b.x
                    dy = a.y - b.y
                    d = math.sqrt(dx * dx + dy * dy)
                    if d < dist:
                        self.canvas.create_line(
                            a.x + a.size / 2, a.y + a.size / 2,
                            b.x + b.size / 2, b.y + b.size / 2,
                            fill=line_col, width=1,
                            tags="pline", stipple="gray25"
                        )

        self._after_id = self.canvas.after(ANIM["particle_tick"], self._tick)
