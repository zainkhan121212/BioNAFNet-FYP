"""
live_preview.py — Live Preview Page (UI Shell)
================================================
Placeholder UI for camera feed / folder-watch preview.
"""

import customtkinter as ctk
import theme as T


class LivePreviewPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=T.BG_MAIN, corner_radius=0, **kwargs)
        self._build()

    def _build(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(title_frame, text="📡  Live Preview",
                     font=T.FONT_HEADING, text_color=T.TEXT).pack(side="left")
        ctk.CTkLabel(title_frame, text="Real-Time Feed",
                     font=T.FONT_TINY, text_color=T.TEXT_MUTED).pack(side="right")

        ctk.CTkFrame(self, height=2, fg_color=T.ACCENT_RED, corner_radius=1).pack(
            fill="x", padx=24, pady=(0, 12))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Controls (left)
        controls = ctk.CTkFrame(content, width=300, fg_color=T.BG_CARD,
                                 corner_radius=16)
        controls.pack(side="left", fill="y", padx=(0, 12))
        controls.pack_propagate(False)

        pad = ctk.CTkFrame(controls, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=16, pady=16)

        # Source selection
        ctk.CTkLabel(pad, text="📹  SOURCE", font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(6, 6))

        self.source_var = ctk.StringVar(value="camera")
        ctk.CTkRadioButton(
            pad, text="Camera Feed", variable=self.source_var, value="camera",
            font=T.FONT_BODY, text_color=T.TEXT_DIM,
            fg_color=T.ACCENT_RED, border_color=T.BORDER,
            hover_color=T.BG_HOVER
        ).pack(anchor="w", pady=3)
        ctk.CTkRadioButton(
            pad, text="Folder Watch", variable=self.source_var, value="folder",
            font=T.FONT_BODY, text_color=T.TEXT_DIM,
            fg_color=T.ACCENT_RED, border_color=T.BORDER,
            hover_color=T.BG_HOVER
        ).pack(anchor="w", pady=3)

        ctk.CTkFrame(pad, height=1, fg_color=T.BORDER).pack(fill="x", pady=14)

        # Camera controls
        ctk.CTkLabel(pad, text="🎛  CAMERA", font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        cam_frame = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        cam_frame.pack(fill="x", pady=(0, 8))
        cf = ctk.CTkFrame(cam_frame, fg_color="transparent")
        cf.pack(padx=14, pady=10)
        ctk.CTkLabel(cf, text="Device Index", font=T.FONT_TINY,
                     text_color=T.TEXT_DIM).pack(anchor="w")
        self.cam_entry = ctk.CTkEntry(cf, height=34, font=T.FONT_BODY,
                                       fg_color=T.BG_DARK, border_color=T.BORDER,
                                       text_color=T.TEXT, corner_radius=8, width=80)
        self.cam_entry.pack(anchor="w")
        self.cam_entry.insert(0, "0")

        ctk.CTkFrame(pad, height=1, fg_color=T.BORDER).pack(fill="x", pady=14)

        # Model for live enhancement
        ctk.CTkLabel(pad, text="✨  ENHANCEMENT MODEL",
                     font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        self.model_combo = ctk.CTkComboBox(
            pad, values=[m["name"] for m in T.MODELS],
            font=T.FONT_BODY, fg_color=T.BG_INPUT,
            border_color=T.BORDER, button_color=T.ACCENT_RED,
            button_hover_color="#d0324f",
            text_color=T.TEXT, dropdown_fg_color=T.BG_CARD,
            dropdown_text_color=T.TEXT, dropdown_hover_color=T.BG_HOVER,
            corner_radius=10, height=36
        )
        self.model_combo.pack(fill="x", pady=(0, 14))

        # Start / Stop
        self.start_btn = ctk.CTkButton(
            pad, text="▶  START PREVIEW", font=T.FONT_SUB,
            fg_color=T.ACCENT_RED, hover_color="#d0324f",
            text_color=T.TEXT, corner_radius=20, height=48,
        )
        self.start_btn.pack(fill="x", pady=(4, 4))

        self.stop_btn = ctk.CTkButton(
            pad, text="⏹  STOP", font=T.FONT_SUB,
            fg_color=T.BG_INPUT, hover_color=T.BG_HOVER,
            text_color=T.TEXT_DIM, corner_radius=20, height=40,
        )
        self.stop_btn.pack(fill="x", pady=(0, 6))

        # FPS display
        self.fps_lbl = ctk.CTkLabel(pad, text="FPS: —", font=T.FONT_MONO,
                                     text_color=T.TEXT_MUTED)
        self.fps_lbl.pack(anchor="w")

        # ── Video placeholder (right) ─────────────────────────
        video_frame = ctk.CTkFrame(content, fg_color=T.BG_CARD, corner_radius=16)
        video_frame.pack(side="left", fill="both", expand=True)

        # Header
        vhdr = ctk.CTkFrame(video_frame, fg_color="transparent")
        vhdr.pack(fill="x", padx=16, pady=(12, 0))
        self.rec_dot = ctk.CTkLabel(vhdr, text="●", font=("Segoe UI", 14),
                                     text_color=T.TEXT_DARK)
        self.rec_dot.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(vhdr, text="PREVIEW", font=T.FONT_SMALL,
                     text_color=T.TEXT_DIM).pack(side="left")
        ctk.CTkLabel(vhdr, text="🔴  LIVE", font=T.FONT_TINY,
                     text_color=T.ACCENT_RED).pack(side="right")

        # Canvas placeholder
        self.video_canvas = ctk.CTkCanvas(
            video_frame, bg=T.BG_DARK, highlightthickness=0
        )
        self.video_canvas.pack(fill="both", expand=True, padx=12, pady=12)

        # Draw placeholder
        self.video_canvas.bind("<Configure>", self._draw_placeholder)

    def _draw_placeholder(self, event=None):
        c = self.video_canvas
        c.delete("all")
        cw = max(c.winfo_width(), 400)
        ch = max(c.winfo_height(), 300)

        # Crosshair
        cx, cy = cw // 2, ch // 2
        r = 60
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      outline=T.TEXT_DARK, width=2, dash=(4, 4))
        c.create_line(cx - r - 20, cy, cx + r + 20, cy,
                      fill=T.TEXT_DARK, width=1)
        c.create_line(cx, cy - r - 20, cx, cy + r + 20,
                      fill=T.TEXT_DARK, width=1)

        c.create_text(cx, cy + r + 40,
                      text="Press START to begin live preview",
                      font=(T.FONT_FAMILY, 12), fill=T.TEXT_MUTED)
        c.create_text(cx, cy + r + 60,
                      text="Camera feed or folder watch mode",
                      font=T.FONT_TINY, fill=T.TEXT_DARK)
