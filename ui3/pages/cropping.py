"""
cropping.py — Cropping Page
==============================
Upload image, specify T/B/L/R pixel amounts, crop & compare.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import theme as T
from widgets.image_viewer import ImageViewer
from utils.image_ops import crop_image


class CroppingPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=T.BG_MAIN, corner_radius=0, **kwargs)
        self.image_path = ""
        self.save_dir = ""
        self.original_img: Image.Image | None = None
        self._build()

    def _build(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(title_frame, text="✂  Precision Cropping",
                     font=T.FONT_HEADING, text_color=T.TEXT).pack(side="left")
        ctk.CTkLabel(title_frame, text="Pixel-Perfect Control",
                     font=T.FONT_TINY, text_color=T.TEXT_MUTED).pack(side="right")

        ctk.CTkFrame(self, height=2, fg_color=T.ACCENT_ORANGE, corner_radius=1).pack(
            fill="x", padx=24, pady=(0, 12))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        controls = ctk.CTkFrame(content, width=300, fg_color=T.BG_CARD,
                                 corner_radius=16)
        controls.pack(side="left", fill="y", padx=(0, 12))
        controls.pack_propagate(False)
        self._build_controls(controls)

        self.viewer = ImageViewer(content)
        self.viewer.right_label.configure(text="Cropped  ✂")
        self.viewer.pack(side="left", fill="both", expand=True)

    def _build_controls(self, parent):
        pad = ctk.CTkFrame(parent, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=16, pady=16)

        self._section(pad, "📂  INPUT")
        ctk.CTkButton(
            pad, text="Upload Image", font=T.FONT_BODY,
            fg_color=T.BG_INPUT, hover_color=T.BG_HOVER,
            text_color=T.TEXT, corner_radius=12, height=40,
            command=self._upload
        ).pack(fill="x", pady=(4, 4))
        self.file_lbl = ctk.CTkLabel(pad, text="No file selected",
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

        # Crop inputs
        self._section(pad, "✂  CROP MARGINS (pixels)")

        self.entries = {}
        grid_frame = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        grid_frame.pack(fill="x", pady=(6, 14))
        gf = ctk.CTkFrame(grid_frame, fg_color="transparent")
        gf.pack(padx=14, pady=14)

        labels = [("Top", 0, 0), ("Bottom", 1, 0), ("Left", 0, 1), ("Right", 1, 1)]
        for lbl, row, col in labels:
            f = ctk.CTkFrame(gf, fg_color="transparent")
            f.grid(row=row, column=col, padx=6, pady=4, sticky="ew")
            ctk.CTkLabel(f, text=lbl, font=T.FONT_TINY,
                         text_color=T.TEXT_DIM).pack(anchor="w")
            entry = ctk.CTkEntry(f, width=100, height=34, font=T.FONT_BODY,
                                  fg_color=T.BG_DARK, border_color=T.BORDER,
                                  text_color=T.TEXT, corner_radius=8,
                                  placeholder_text="0")
            entry.pack(fill="x")
            entry.insert(0, "0")
            self.entries[lbl.lower()] = entry

        # Image dimensions display
        self.dim_lbl = ctk.CTkLabel(pad, text="", font=T.FONT_TINY,
                                     text_color=T.TEXT_MUTED)
        self.dim_lbl.pack(anchor="w", pady=(0, 10))

        # Crop button
        self.crop_btn = ctk.CTkButton(
            pad, text="✂  CROP IMAGE", font=T.FONT_SUB,
            fg_color=T.ACCENT_ORANGE, hover_color="#e07530",
            text_color=T.BG_DARK, corner_radius=20, height=48,
            command=self._crop
        )
        self.crop_btn.pack(fill="x", pady=(4, 6))

        self.status_lbl = ctk.CTkLabel(pad, text="", font=T.FONT_TINY,
                                        text_color=T.ACCENT_ORANGE)
        self.status_lbl.pack(anchor="w")

    def _section(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(6, 0))

    def _upload(self):
        f = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if f:
            self.image_path = f
            self.original_img = Image.open(f).copy()
            self.file_lbl.configure(text=os.path.basename(f))
            self.dim_lbl.configure(
                text=f"Dimensions: {self.original_img.width} × {self.original_img.height} px")
            self.viewer.set_original(self.original_img)

    def _select_save(self):
        d = filedialog.askdirectory()
        if d:
            self.save_dir = d
            self.save_lbl.configure(text=os.path.basename(d) or d)

    def _crop(self):
        if self.original_img is None:
            messagebox.showwarning("No Image", "Upload an image first.")
            return
        try:
            top = int(self.entries["top"].get())
            bottom = int(self.entries["bottom"].get())
            left = int(self.entries["left"].get())
            right = int(self.entries["right"].get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Crop values must be integers.")
            return

        result = crop_image(self.original_img, top, bottom, left, right)

        if self.save_dir:
            name = f"cropped_{os.path.basename(self.image_path)}"
            result.save(os.path.join(self.save_dir, name))

        self.viewer.set_images(self.original_img, result)
        self.status_lbl.configure(
            text=f"✅ Cropped to {result.width}×{result.height} px")
