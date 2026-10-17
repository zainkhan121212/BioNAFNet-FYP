"""
resizing.py — Resizing Page
==============================
Upload, presets + custom dimensions, percentage scaling, resize & compare.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import theme as T
from widgets.image_viewer import ImageViewer
from utils.image_ops import resize_image


PRESETS = [
    ("HD",    1280,  720),
    ("FHD",   1920, 1080),
    ("2K",    2560, 1440),
    ("4K",    3840, 2160),
    ("Square 512",  512,  512),
    ("Square 1024", 1024, 1024),
]


class ResizingPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=T.BG_MAIN, corner_radius=0, **kwargs)
        self.image_path = ""
        self.save_dir = ""
        self.original_img: Image.Image | None = None
        self._build()

    def _build(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(title_frame, text="📐  Image Resizing",
                     font=T.FONT_HEADING, text_color=T.TEXT).pack(side="left")
        ctk.CTkLabel(title_frame, text="Presets & Custom",
                     font=T.FONT_TINY, text_color=T.TEXT_MUTED).pack(side="right")

        ctk.CTkFrame(self, height=2, fg_color=T.ACCENT_GREEN, corner_radius=1).pack(
            fill="x", padx=24, pady=(0, 12))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        controls = ctk.CTkFrame(content, width=300, fg_color=T.BG_CARD,
                                 corner_radius=16)
        controls.pack(side="left", fill="y", padx=(0, 12))
        controls.pack_propagate(False)
        self._build_controls(controls)

        self.viewer = ImageViewer(content)
        self.viewer.right_label.configure(text="Resized  📐")
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

        # Presets
        self._section(pad, "📏  PRESETS")
        preset_frame = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        preset_frame.pack(fill="x", pady=(4, 14))
        pf = ctk.CTkFrame(preset_frame, fg_color="transparent")
        pf.pack(padx=10, pady=10)

        row_frame = None
        for i, (label, w, h) in enumerate(PRESETS):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(pf, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
            ctk.CTkButton(
                row_frame, text=f"{label}\n{w}×{h}", font=T.FONT_TINY,
                fg_color="transparent", hover_color=T.BG_HOVER,
                text_color=T.TEXT_DIM, corner_radius=8, height=46, width=110,
                command=lambda ww=w, hh=h: self._set_custom(ww, hh)
            ).pack(side="left", padx=2, fill="x", expand=True)

        # Custom
        self._section(pad, "🔧  CUSTOM SIZE")
        custom_frame = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        custom_frame.pack(fill="x", pady=(4, 4))
        cf = ctk.CTkFrame(custom_frame, fg_color="transparent")
        cf.pack(padx=14, pady=10)

        wf = ctk.CTkFrame(cf, fg_color="transparent")
        wf.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(wf, text="Width", font=T.FONT_TINY,
                     text_color=T.TEXT_DIM).pack(anchor="w")
        self.w_entry = ctk.CTkEntry(wf, height=34, font=T.FONT_BODY,
                                     fg_color=T.BG_DARK, border_color=T.BORDER,
                                     text_color=T.TEXT, corner_radius=8)
        self.w_entry.pack(fill="x")
        self.w_entry.insert(0, "1920")

        hf = ctk.CTkFrame(cf, fg_color="transparent")
        hf.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(hf, text="Height", font=T.FONT_TINY,
                     text_color=T.TEXT_DIM).pack(anchor="w")
        self.h_entry = ctk.CTkEntry(hf, height=34, font=T.FONT_BODY,
                                     fg_color=T.BG_DARK, border_color=T.BORDER,
                                     text_color=T.TEXT, corner_radius=8)
        self.h_entry.pack(fill="x")
        self.h_entry.insert(0, "1080")

        # Percentage slider
        self._section(pad, "📊  PERCENTAGE SCALE")
        sf = ctk.CTkFrame(pad, fg_color=T.BG_INPUT, corner_radius=12)
        sf.pack(fill="x", pady=(4, 14))
        si = ctk.CTkFrame(sf, fg_color="transparent")
        si.pack(padx=14, pady=10)

        self.pct_var = ctk.IntVar(value=100)
        self.pct_slider = ctk.CTkSlider(
            si, from_=10, to=200, variable=self.pct_var,
            progress_color=T.ACCENT_GREEN, button_color=T.TEXT,
            fg_color=T.TEXT_DARK, width=180,
            command=self._on_pct_slide
        )
        self.pct_slider.pack(side="left")
        self.pct_lbl = ctk.CTkLabel(si, text="100%", font=T.FONT_SUB,
                                     text_color=T.ACCENT_GREEN, width=50)
        self.pct_lbl.pack(side="left", padx=(8, 0))

        # Resize button
        self.resize_btn = ctk.CTkButton(
            pad, text="📐  RESIZE IMAGE", font=T.FONT_SUB,
            fg_color=T.ACCENT_GREEN, hover_color="#22b060",
            text_color=T.BG_DARK, corner_radius=20, height=48,
            command=self._resize
        )
        self.resize_btn.pack(fill="x", pady=(4, 6))
        self.status_lbl = ctk.CTkLabel(pad, text="", font=T.FONT_TINY,
                                        text_color=T.ACCENT_GREEN)
        self.status_lbl.pack(anchor="w")

    def _section(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED).pack(anchor="w", pady=(6, 0))

    def _on_pct_slide(self, val):
        pct = int(val)
        self.pct_lbl.configure(text=f"{pct}%")
        if self.original_img:
            nw = int(self.original_img.width * pct / 100)
            nh = int(self.original_img.height * pct / 100)
            self.w_entry.delete(0, "end")
            self.w_entry.insert(0, str(nw))
            self.h_entry.delete(0, "end")
            self.h_entry.insert(0, str(nh))

    def _set_custom(self, w, h):
        self.w_entry.delete(0, "end")
        self.w_entry.insert(0, str(w))
        self.h_entry.delete(0, "end")
        self.h_entry.insert(0, str(h))

    def _upload(self):
        f = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if f:
            self.image_path = f
            self.original_img = Image.open(f).copy()
            self.file_lbl.configure(text=os.path.basename(f))
            self.viewer.set_original(self.original_img)

    def _select_save(self):
        d = filedialog.askdirectory()
        if d:
            self.save_dir = d
            self.save_lbl.configure(text=os.path.basename(d) or d)

    def _resize(self):
        if self.original_img is None:
            messagebox.showwarning("No Image", "Upload an image first.")
            return
        try:
            w = int(self.w_entry.get())
            h = int(self.h_entry.get())
        except ValueError:
            messagebox.showerror("Invalid", "Width and height must be integers.")
            return
        if w < 1 or h < 1:
            messagebox.showerror("Invalid", "Dimensions must be positive.")
            return

        result = resize_image(self.original_img, w, h)
        if self.save_dir:
            name = f"resized_{w}x{h}_{os.path.basename(self.image_path)}"
            result.save(os.path.join(self.save_dir, name))

        self.viewer.set_images(self.original_img, result)
        self.status_lbl.configure(text=f"✅ Resized to {w}×{h} px")
