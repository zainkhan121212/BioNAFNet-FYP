"""
enhance.py — Enhance Page
============================
Upload, model selection, CPU/GPU toggle, enhance, split-comparison viewer.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import theme as T
from widgets.image_viewer import ImageViewer
from utils.image_ops import enhance_image


class EnhancePage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=T.BG_MAIN, corner_radius=0, **kwargs)
        self.uploaded_paths: list[str] = []
        self.save_dir = ""
        self.current_idx = 0
        self.original_img: Image.Image | None = None
        self.enhanced_img: Image.Image | None = None
        self._build()

    def _build(self):
        # ── Title ──────────────────────────────────────────────
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(title_frame, text="✦  Image Enhancement",
                     font=T.FONT_HEADING, text_color=T.TEXT).pack(side="left")
        ctk.CTkLabel(title_frame, text="Low-Light AI Models",
                     font=T.FONT_TINY, text_color=T.TEXT_MUTED).pack(side="right")

        # Accent bar
        ctk.CTkFrame(self, height=2, fg_color=T.ACCENT, corner_radius=1).pack(
            fill="x", padx=24, pady=(0, 12))

        # ── Content split: controls (left) + viewer (right) ───
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Controls panel (left)
        controls = ctk.CTkFrame(content, width=300, fg_color=T.BG_CARD,
                                 corner_radius=16)
        controls.pack(side="left", fill="y", padx=(0, 12))
        controls.pack_propagate(False)
        self._build_controls(controls)

        # Viewer (right)
        self.viewer = ImageViewer(content)
        self.viewer.pack(side="left", fill="both", expand=True)

    def _build_controls(self, parent):
        pad = ctk.CTkFrame(parent, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=16, pady=16)

        # ── Upload ─────────────────────────────────────────────
        self._section_label(pad, "📂  INPUT")
        self.upload_btn = ctk.CTkButton(
            pad, text="Upload Image(s)", font=T.FONT_BODY,
            fg_color=T.BG_INPUT, hover_color=T.BG_HOVER,
            text_color=T.TEXT, corner_radius=12, height=40,
            command=self._upload
        )
        self.upload_btn.pack(fill="x", pady=(4, 4))

        self.file_lbl = ctk.CTkLabel(pad, text="No files selected",
                                      font=T.FONT_TINY, text_color=T.TEXT_MUTED)
        self.file_lbl.pack(anchor="w", pady=(0, 10))

        self.save_btn = ctk.CTkButton(
            pad, text="Select Save Directory", font=T.FONT_BODY,
            fg_color=T.BG_INPUT, hover_color=T.BG_HOVER,
            text_color=T.TEXT, corner_radius=12, height=40,
            command=self._select_save
        )
        self.save_btn.pack(fill="x", pady=(0, 4))

        self.save_lbl = ctk.CTkLabel(pad, text="No directory selected",
                                      font=T.FONT_TINY, text_color=T.TEXT_MUTED)
        self.save_lbl.pack(anchor="w", pady=(0, 14))

        # ── Model Selection ────────────────────────────────────
        self._section_label(pad, "🧠  MODEL")

        self.model_var = ctk.StringVar(value=T.MODELS[0]["id"])
        model_scroll = ctk.CTkScrollableFrame(pad, height=140,
                                               fg_color=T.BG_INPUT,
                                               corner_radius=12)
        model_scroll.pack(fill="x", pady=(4, 14))

        self._model_btns = {}
        for m in T.MODELS:
            btn = ctk.CTkButton(
                model_scroll,
                text=f"  {m['icon']}  {m['name']}",
                font=T.FONT_SMALL, anchor="w",
                fg_color="transparent",
                hover_color=T.BG_HOVER,
                text_color=T.TEXT_DIM,
                corner_radius=8, height=34,
                command=lambda mid=m["id"]: self._select_model(mid)
            )
            btn.pack(fill="x", pady=1)
            self._model_btns[m["id"]] = btn

        # Highlight default
        self._select_model(T.MODELS[0]["id"])

        # ── Hardware Toggle ────────────────────────────────────
        self._section_label(pad, "⚙  HARDWARE")

        hw_frame = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        hw_frame.pack(fill="x", pady=(4, 14))
        hw_inner = ctk.CTkFrame(hw_frame, fg_color="transparent")
        hw_inner.pack(padx=12, pady=10)

        ctk.CTkLabel(hw_inner, text="CPU", font=T.FONT_SMALL,
                     text_color=T.TEXT_DIM).pack(side="left", padx=(0, 8))
        self.hw_switch = ctk.CTkSwitch(
            hw_inner, text="", width=50,
            progress_color=T.ACCENT,
            button_color=T.TEXT,
            fg_color=T.TEXT_DARK,
            onvalue=1, offvalue=0
        )
        self.hw_switch.pack(side="left")
        ctk.CTkLabel(hw_inner, text="GPU", font=T.FONT_SMALL,
                     text_color=T.ACCENT).pack(side="left", padx=(8, 0))

        # ── Enhance Button ─────────────────────────────────────
        self.enhance_btn = ctk.CTkButton(
            pad, text="⚡  ENHANCE IMAGE", font=T.FONT_SUB,
            fg_color=T.ACCENT, hover_color=T.ACCENT_DIM,
            text_color=T.BG_DARK, corner_radius=20, height=48,
            command=self._enhance
        )
        self.enhance_btn.pack(fill="x", pady=(4, 6))

        # Progress
        self.progress = ctk.CTkProgressBar(pad, height=6, corner_radius=3,
                                            fg_color=T.BG_INPUT,
                                            progress_color=T.ACCENT)
        self.progress.pack(fill="x", pady=(0, 4))
        self.progress.set(0)

        self.status_lbl = ctk.CTkLabel(pad, text="", font=T.FONT_TINY,
                                        text_color=T.ACCENT)
        self.status_lbl.pack(anchor="w")

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(6, 0))

    def _upload(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if files:
            self.uploaded_paths = list(files)
            self.current_idx = 0
            n = len(self.uploaded_paths)
            self.file_lbl.configure(text=f"{n} image{'s' if n > 1 else ''} selected")
            self._load_current()

    def _select_save(self):
        d = filedialog.askdirectory(title="Select Save Directory")
        if d:
            self.save_dir = d
            self.save_lbl.configure(text=os.path.basename(d) or d)

    def _select_model(self, mid):
        self.model_var.set(mid)
        for k, btn in self._model_btns.items():
            if k == mid:
                btn.configure(fg_color=T.BG_HOVER, text_color=T.ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=T.TEXT_DIM)

    def _load_current(self):
        if not self.uploaded_paths:
            return
        path = self.uploaded_paths[self.current_idx]
        self.original_img = Image.open(path).copy()
        self.enhanced_img = None
        self.viewer.set_original(self.original_img)

    def _enhance(self):
        if not self.uploaded_paths:
            messagebox.showwarning("No Images", "Please upload images first.")
            return
        self.enhance_btn.configure(state="disabled", text="Processing...")
        self.progress.set(0)
        threading.Thread(target=self._enhance_thread, daemon=True).start()

    def _enhance_thread(self):
        total = len(self.uploaded_paths)
        model_id = self.model_var.get()
        for i, path in enumerate(self.uploaded_paths):
            img = Image.open(path).convert("RGB")
            result = enhance_image(img, model_id)

            # Save if save dir set
            if self.save_dir:
                name = f"enhanced_{os.path.basename(path)}"
                result.save(os.path.join(self.save_dir, name))

            # Update progress
            self.after(0, lambda p=(i + 1) / total: self.progress.set(p))
            self.after(0, lambda c=i + 1: self.status_lbl.configure(
                text=f"Processed {c}/{total}"))

            if i == self.current_idx:
                self.enhanced_img = result
                self.after(0, lambda: self.viewer.set_images(
                    self.original_img, self.enhanced_img))

        self.after(0, self._enhance_done)

    def _enhance_done(self):
        self.enhance_btn.configure(state="normal", text="⚡  ENHANCE IMAGE")
        self.status_lbl.configure(text="✅ Enhancement complete!")
