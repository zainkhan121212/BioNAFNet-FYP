"""
particles.py — Floating GPU Particles
=======================================
30 particles float upward with glowing colors.
"""

import random
import tkinter as tk
import theme as T


class Particle:
    __slots__ = ("x", "y", "vy", "size", "color", "oid")

    def __init__(self, x, y, vy, size, color, oid=None):
        self.x, self.y, self.vy, self.size, self.color = x, y, vy, size, color
        self.oid = oid


class ParticleSystem:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.particles: list[Particle] = []
        self._running = False
        self._aid = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._spawn()
        self._tick()

    def stop(self):
        self._running = False
        if self._aid:
            self.canvas.after_cancel(self._aid)
        self.canvas.delete("particle")
        self.particles.clear()

    def _spawn(self):
        w = max(self.canvas.winfo_width(), 800)
        h = max(self.canvas.winfo_height(), 800)
        for _ in range(30):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            vy = -(0.4 + random.random() * 1.2)
            sz = 1 + random.random() * 3
            col = random.choice(T.PARTICLE_COLORS)
            oid = self.canvas.create_oval(
                x, y, x + sz, y + sz,
                fill=col, outline="", tags="particle"
            )
            self.particles.append(Particle(x, y, vy, sz, col, oid))

    def _tick(self):
        if not self._running:
            return
        h = max(self.canvas.winfo_height(), 800)
        for p in self.particles:
            p.y += p.vy
            if p.y < -10:
                p.y = h + 10
                p.x = random.uniform(0, max(self.canvas.winfo_width(), 800))
            self.canvas.coords(p.oid, p.x, p.y, p.x + p.size, p.y + p.size)
        self._aid = self.canvas.after(T.ANIM["particle_tick"], self._tick)
