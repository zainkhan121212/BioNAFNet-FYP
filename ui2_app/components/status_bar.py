"""
status_bar.py — Neumorphic Status Bar
=======================================
Clean bottom bar with GPU indicator, image count, file size.
"""

import tkinter as tk
import theme as T


class StatusBar:
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=T.BG, height=30)
        self.frame.pack(fill=tk.X)
        self.frame.pack_propagate(False)
        self._build()

    def _build(self):
        # Subtle top separator
        tk.Frame(self.frame, height=1, bg=T.BG_LIGHT).pack(fill=tk.X)

        inner = tk.Frame(self.frame, bg=T.BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=14)
        self._inner = inner

        # Left
        left = tk.Frame(inner, bg=T.BG)
        left.pack(side=tk.LEFT, pady=3)
        self._left = left

        self.img_count = tk.Label(left, text="📂 0 images", font=T.FONT_MONO_SM,
                                   bg=T.BG, fg=T.TEXT3)
        self.img_count.pack(side=tk.LEFT, padx=(0, 14))

        self.file_info = tk.Label(left, text="", font=T.FONT_MONO_SM,
                                   bg=T.BG, fg=T.TEXT3)
        self.file_info.pack(side=tk.LEFT)

        # Right
        right = tk.Frame(inner, bg=T.BG)
        right.pack(side=tk.RIGHT, pady=3)
        self._right = right

        self.gpu_status = tk.Label(right, text="🖥 CPU Mode", font=T.FONT_MONO_SM,
                                    bg=T.BG, fg=T.TEXT3)
        self.gpu_status.pack(side=tk.LEFT, padx=8)

        self.ready_lbl = tk.Label(right, text="⏱ Ready", font=T.FONT_MONO_SM,
                                   bg=T.BG, fg=T.TEXT3)
        self.ready_lbl.pack(side=tk.LEFT, padx=8)

        # GPU online dot + label
        self.gpu_dot_frame = tk.Frame(right, bg=T.BG)
        self.gpu_dot = tk.Canvas(self.gpu_dot_frame, width=16, height=16,
                                  bg=T.BG, highlightthickness=0)
        self.gpu_dot.pack(side=tk.LEFT)
        self.gpu_dot.create_oval(4, 4, 12, 12, fill=T.GREEN,
                                  outline="", tags="dot")
        self.gpu_online = tk.Label(self.gpu_dot_frame, text="GPU Online",
                                    font=T.FONT_MONO_SM, bg=T.BG, fg=T.GREEN)
        self.gpu_online.pack(side=tk.LEFT, padx=2)

    def update_count(self, n, total_bytes=0):
        mb = total_bytes / (1024 * 1024) if total_bytes else 0
        self.img_count.config(text=f"📂 {n} image{'s' if n != 1 else ''}")
        self.file_info.config(text=f"💾 {mb:.2f} MB" if mb else "")

    def set_status(self, text):
        self.ready_lbl.config(text=f"⏱ {text}")

    def apply_theme(self):
        gpu = self.app.gpu_enabled.get()
        if gpu:
            self.gpu_status.config(text="⚡ CUDA Accelerated", fg=T.PURPLE)
            self.gpu_dot_frame.pack(side=tk.LEFT, padx=8)
        else:
            self.gpu_status.config(text="🖥 CPU Mode", fg=T.TEXT3)
            self.gpu_dot_frame.pack_forget()
