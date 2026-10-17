"""
augmentation.py — Augmentation Page
=======================================
Upload multiple images, specify count (max 4), augment & compare.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import theme as T
from widgets.image_viewer import ImageViewer
from utils.image_ops import augment_image


class AugmentationPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=T.BG_MAIN, corner_radius=0, **kwargs)
        self.uploaded_paths: list[str] = []
        self.save_dir = ""
        self._build()

    def _build(self):
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(title_frame, text="🔀  Data Augmentation",
                     font=T.FONT_HEADING, text_color=T.TEXT).pack(side="left")
        ctk.CTkLabel(title_frame, text="Generate Training Variants",
                     font=T.FONT_TINY, text_color=T.TEXT_MUTED).pack(side="right")

        ctk.CTkFrame(self, height=2, fg_color=T.ACCENT_PURPLE, corner_radius=1).pack(
            fill="x", padx=24, pady=(0, 12))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Controls
        controls = ctk.CTkFrame(content, width=300, fg_color=T.BG_CARD,
                                 corner_radius=16)
        controls.pack(side="left", fill="y", padx=(0, 12))
        controls.pack_propagate(False)
        self._build_controls(controls)

        # Viewer
        self.viewer = ImageViewer(content)
        self.viewer.right_label.configure(text="Augmented  🔀")
        self.viewer.pack(side="left", fill="both", expand=True)

    def _build_controls(self, parent):
        pad = ctk.CTkFrame(parent, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=16, pady=16)

        # Upload
        self._section(pad, "📂  INPUT")
        ctk.CTkButton(
            pad, text="Upload Image(s)", font=T.FONT_BODY,
            fg_color=T.BG_INPUT, hover_color=T.BG_HOVER,
            text_color=T.TEXT, corner_radius=12, height=40,
            command=self._upload
        ).pack(fill="x", pady=(4, 4))
        self.file_lbl = ctk.CTkLabel(pad, text="No files selected",
                                      font=T.FONT_TINY, text_color=T.TEXT_MUTED)
        self.file_lbl.pack(anchor="w", pady=(0, 6))

        ctk.CTkButton(
            pad, text="Select Save Folder", font=T.FONT_BODY,
            fg_color=T.BG_INPUT, hover_color=T.BG_HOVER,
            text_color=T.TEXT, corner_radius=12, height=40,
            command=self._select_save
        ).pack(fill="x", pady=(0, 4))
        self.save_lbl = ctk.CTkLabel(pad, text="No folder selected",
                                      font=T.FONT_TINY, text_color=T.TEXT_MUTED)
        self.save_lbl.pack(anchor="w", pady=(0, 14))

        # Count
        self._section(pad, "🔢  AUGMENTATION COUNT")
        ctk.CTkLabel(pad, text="How many times per image? (1 – 4)",
                     font=T.FONT_TINY, text_color=T.TEXT_DIM).pack(anchor="w", pady=(4, 4))

        slider_frame = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        slider_frame.pack(fill="x", pady=(0, 4))
        sf = ctk.CTkFrame(slider_frame, fg_color="transparent")
        sf.pack(padx=14, pady=10)

        self.count_var = ctk.IntVar(value=2)
        self.count_slider = ctk.CTkSlider(
            sf, from_=1, to=4, number_of_steps=3,
            variable=self.count_var,
            progress_color=T.ACCENT_PURPLE,
            button_color=T.TEXT,
            fg_color=T.TEXT_DARK,
            width=200,
            command=self._on_slider
        )
        self.count_slider.pack(side="left")
        self.count_lbl = ctk.CTkLabel(sf, text="2x", font=T.FONT_SUB,
                                       text_color=T.ACCENT_PURPLE, width=40)
        self.count_lbl.pack(side="left", padx=(10, 0))

        # Augment button
        ctk.CTkFrame(pad, fg_color="transparent", height=20).pack()
        self.aug_btn = ctk.CTkButton(
            pad, text="🔀  AUGMENT IMAGES", font=T.FONT_SUB,
            fg_color=T.ACCENT_PURPLE, hover_color="#7025c2",
            text_color=T.TEXT, corner_radius=20, height=48,
            command=self._augment
        )
        self.aug_btn.pack(fill="x", pady=(4, 6))

        self.progress = ctk.CTkProgressBar(pad, height=6, corner_radius=3,
                                            fg_color=T.BG_INPUT,
                                            progress_color=T.ACCENT_PURPLE)
        self.progress.pack(fill="x", pady=(0, 4))
        self.progress.set(0)
        self.status_lbl = ctk.CTkLabel(pad, text="", font=T.FONT_TINY,
                                        text_color=T.ACCENT_PURPLE)
        self.status_lbl.pack(anchor="w")

    def _section(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(6, 0))

    def _on_slider(self, val):
        self.count_lbl.configure(text=f"{int(val)}x")

    def _upload(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if files:
            self.uploaded_paths = list(files)
            self.file_lbl.configure(text=f"{len(files)} image(s) selected")
            img = Image.open(files[0])
            self.viewer.set_original(img)

    def _select_save(self):
        d = filedialog.askdirectory()
        if d:
            self.save_dir = d
            self.save_lbl.configure(text=os.path.basename(d) or d)

    def _augment(self):
        if not self.uploaded_paths:
            messagebox.showwarning("No Images", "Upload images first.")
            return
        if not self.save_dir:
            messagebox.showwarning("No Folder", "Select a save folder.")
            return
        self.aug_btn.configure(state="disabled", text="Processing...")
        self.progress.set(0)
        threading.Thread(target=self._aug_thread, daemon=True).start()

    def _aug_thread(self):
        count = self.count_var.get()
        total = len(self.uploaded_paths) * count
        done = 0
        first_result = None
        for path in self.uploaded_paths:
            img = Image.open(path).convert("RGB")
            base = os.path.splitext(os.path.basename(path))[0]
            for i in range(count):
                result = augment_image(img, i)
                result.save(os.path.join(self.save_dir, f"{base}_aug{i + 1}.png"))
                done += 1
                if first_result is None:
                    first_result = result
                self.after(0, lambda p=done / total: self.progress.set(p))
                self.after(0, lambda c=done: self.status_lbl.configure(
                    text=f"Generated {c}/{total}"))

        if first_result:
            orig = Image.open(self.uploaded_paths[0])
            self.after(0, lambda: self.viewer.set_images(orig, first_result))
        self.after(0, self._aug_done)

    def _aug_done(self):
        self.aug_btn.configure(state="normal", text="🔀  AUGMENT IMAGES")
        self.status_lbl.configure(text="✅ Augmentation complete!")
