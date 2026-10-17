"""
image_viewer.py — Side-by-Side / Split Comparison Widget
==========================================================
Reusable before/after viewer with drag-slider for split mode.
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import theme as T


class ImageViewer(ctk.CTkFrame):
    """Displays original vs processed image with a draggable split slider."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=T.BG_CARD, corner_radius=16, **kwargs)

        self.original_pil = None
        self.processed_pil = None
        self._photo_left = None
        self._photo_right = None
        self._split_x = 0.5  # 0.0 to 1.0

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 0))

        self.left_label = ctk.CTkLabel(hdr, text="📷  Original", font=T.FONT_SMALL,
                                        text_color=T.TEXT_DIM)
        self.left_label.pack(side="left")
        self.right_label = ctk.CTkLabel(hdr, text="Enhanced  ✨", font=T.FONT_SMALL,
                                         text_color=T.ACCENT)
        self.right_label.pack(side="right")

        # Canvas
        self.canvas = ctk.CTkCanvas(self, bg=T.BG_DARK, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=12)

        # Bindings
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Button-1>", self._on_drag)
        self.canvas.bind("<Configure>", self._on_resize)

        # Placeholder
        self._draw_placeholder()

    def set_original(self, pil_img: Image.Image):
        self.original_pil = pil_img.copy()
        self._redraw()

    def set_processed(self, pil_img: Image.Image):
        self.processed_pil = pil_img.copy()
        self._redraw()

    def set_images(self, original: Image.Image, processed: Image.Image):
        self.original_pil = original.copy()
        self.processed_pil = processed.copy()
        self._redraw()

    def clear(self):
        self.original_pil = None
        self.processed_pil = None
        self.canvas.delete("all")
        self._draw_placeholder()

    def _on_drag(self, event):
        cw = self.canvas.winfo_width()
        if cw > 0:
            self._split_x = max(0.05, min(0.95, event.x / cw))
            self._redraw()

    def _on_resize(self, event=None):
        self._redraw()

    def _draw_placeholder(self):
        self.canvas.delete("all")
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)
        self.canvas.create_text(
            cw // 2, ch // 2,
            text="🖼️\n\nUpload an image to begin\nDrag the slider to compare",
            font=(T.FONT_FAMILY, 13), fill=T.TEXT_MUTED,
            justify="center"
        )

    def _redraw(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        self.canvas.delete("all")

        if self.original_pil is None and self.processed_pil is None:
            self._draw_placeholder()
            return

        # Fit image to canvas
        def fit(pil_img):
            if pil_img is None:
                return None
            ratio = min(cw / pil_img.width, ch / pil_img.height)
            nw, nh = int(pil_img.width * ratio), int(pil_img.height * ratio)
            return pil_img.resize((nw, nh), Image.Resampling.LANCZOS)

        orig_fit = fit(self.original_pil)
        proc_fit = fit(self.processed_pil) if self.processed_pil else orig_fit

        if orig_fit is None:
            return

        iw, ih = orig_fit.size
        ox = (cw - iw) // 2
        oy = (ch - ih) // 2

        # If we have both images, do split view
        if self.processed_pil is not None:
            split_px = int(iw * self._split_x)

            # Left half (original)
            left_crop = orig_fit.crop((0, 0, split_px, ih))
            self._photo_left = ImageTk.PhotoImage(left_crop)
            self.canvas.create_image(ox, oy, image=self._photo_left, anchor="nw")

            # Right half (processed)
            right_crop = proc_fit.crop((split_px, 0, iw, ih))
            self._photo_right = ImageTk.PhotoImage(right_crop)
            self.canvas.create_image(ox + split_px, oy, image=self._photo_right, anchor="nw")

            # Slider line
            sx = ox + split_px
            self.canvas.create_line(sx, oy, sx, oy + ih, fill=T.ACCENT, width=3)
            # Slider handle
            self.canvas.create_oval(sx - 12, oy + ih // 2 - 12,
                                     sx + 12, oy + ih // 2 + 12,
                                     fill=T.ACCENT, outline=T.BG_DARK, width=2)
            self.canvas.create_text(sx, oy + ih // 2, text="◀▶",
                                     font=("Segoe UI", 8), fill=T.BG_DARK)

            # Labels
            self.canvas.create_text(ox + 10, oy + 10, text="ORIGINAL",
                                     font=T.FONT_TINY, fill=T.TEXT_DIM, anchor="nw")
            self.canvas.create_text(ox + iw - 10, oy + 10, text="ENHANCED",
                                     font=T.FONT_TINY, fill=T.ACCENT, anchor="ne")
        else:
            # Single image
            self._photo_left = ImageTk.PhotoImage(orig_fit)
            self.canvas.create_image(ox, oy, image=self._photo_left, anchor="nw")
