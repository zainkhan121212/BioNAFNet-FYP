"""
app.py — Main ImageEnhancer Pro Application Window
=====================================================
Assembles all components, animations, and manages global state.
Uses ttkbootstrap for modern themed widgets and pywinstyles
for Windows acrylic glassmorphism.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime
from PIL import Image

# ttkbootstrap for modern theming
import ttkbootstrap as ttk

# Windows acrylic glass effect
try:
    import pywinstyles
    HAS_PYWINSTYLES = True
except ImportError:
    HAS_PYWINSTYLES = False

# ── local modules ──────────────────────────────────────────────────
from theme import get_theme, LIGHT, DARK, ANIM, GPU_OVERLAY
from components.header import Header
from components.sidebar_left import SidebarLeft
from components.center_panel import CenterPanel
from components.sidebar_right import SidebarRight
from components.bottom_toolbar import BottomToolbar
from components import dialogs
from animations.particle_system import ParticleSystem
from animations.glow_engine import GlowEngine
from animations.gpu_awakening import GPUAwakening
from utils.image_processing import MODELS


class ImageEnhancerPro(ttk.Window):
    """Main application window — glassmorphism, particles, GPU awakening."""

    def __init__(self):
        super().__init__(
            title="ImageEnhancer Pro — Advanced Image Processing Suite",
            themename="superhero",
            size=(1420, 920),
            minsize=(1200, 800),
        )

        # ── state variables ────────────────────────────────────────
        self.dark_mode       = tk.BooleanVar(value=True)
        self.gpu_enabled     = tk.BooleanVar(value=False)
        self.selected_model  = tk.StringVar(value="A")
        self.uploaded_images: list[str] = []
        self.current_image_index = 0
        self.enhanced_images: dict[int, Image.Image] = {}
        self.save_path       = ""

        # ── build UI layers ────────────────────────────────────────
        self._build_layers()

        # ── animations ─────────────────────────────────────────────
        self.glow = GlowEngine(self)
        self.particles = ParticleSystem(self.bg_canvas, self._current_theme)
        self.awakening = GPUAwakening(
            self, self.bg_canvas, self.particles, self.glow,
            status_callback=self.set_status
        )

        # register widgets to glow engine
        self.glow.register_logo(self.header.logo_label)
        self.glow.register_gpu_indicator(self.header.gpu_indicator)
        # register the glass cards for GPU glow pulsation
        self.glow.register_glow_panel(self.left.upload_card)
        self.glow.register_glow_panel(self.left.save_card)
        self.glow.register_glow_panel(self.left.list_card)
        self.glow.register_glow_panel(self.center.viewer)
        self.glow.register_glow_panel(self.right.models_card)
        self.glow.register_glow_panel(self.right.enhance_card)
        self.glow.register_glow_panel(self.right.info_card)
        self.glow.register_glow_panel(self.toolbar.frame)

        # start base animations
        self.glow.start()
        self.particles.start(gpu_mode=False)

        # ── apply theme ────────────────────────────────────────────
        self._apply_theme_all()

        # ── Windows acrylic glass ──────────────────────────────────
        if HAS_PYWINSTYLES and sys.platform == "win32":
            try:
                pywinstyles.apply_style(self, "dark")
                self.update_idletasks()
            except Exception:
                pass

    # ══════════════════════════════════════════════════════════════
    # Layout
    # ══════════════════════════════════════════════════════════════
    def _build_layers(self):
        t = self._current_theme()

        # root container
        self.main_container = tk.Frame(self, bg=t["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # background canvas for particles (lowest layer)
        self.bg_canvas = tk.Canvas(
            self.main_container, highlightthickness=0, bg=t["bg"]
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # ── header ─────────────────────────────────────────────────
        self.header = Header(self.main_container, self)
        self.header.frame.lift()

        # ── content area ───────────────────────────────────────────
        self.content = tk.Frame(self.main_container, bg=t["bg"])
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.content.lift()

        self.left   = SidebarLeft(self.content, self)
        self.right  = SidebarRight(self.content, self)
        self.center = CenterPanel(self.content, self)

        # ── bottom toolbar ─────────────────────────────────────────
        self.toolbar = BottomToolbar(self.main_container, self)
        self.toolbar.frame.lift()

    # ══════════════════════════════════════════════════════════════
    # Theme
    # ══════════════════════════════════════════════════════════════
    def _current_theme(self) -> dict:
        return get_theme(self.dark_mode.get())

    def toggle_theme(self):
        self.dark_mode.set(not self.dark_mode.get())
        # switch ttkbootstrap theme
        theme_name = DARK["name"] if self.dark_mode.get() else LIGHT["name"]
        try:
            self.style.theme_use(theme_name)
        except Exception:
            pass
        self._apply_theme_all()

    def _apply_theme_all(self):
        t = self._current_theme()
        self.main_container.config(bg=t["bg"])
        self.bg_canvas.config(bg=t["bg"])
        self.content.config(bg=t["bg"])
        self.header.apply_theme()
        self.left.apply_theme()
        self.center.apply_theme()
        self.right.apply_theme()
        self.toolbar.apply_theme()

    # ══════════════════════════════════════════════════════════════
    # GPU Toggle
    # ══════════════════════════════════════════════════════════════
    def toggle_gpu(self):
        self.gpu_enabled.set(not self.gpu_enabled.get())
        if self.gpu_enabled.get():
            self.awakening.awaken()
        else:
            self.awakening.calm()
        # refresh theme to pick up GPU accent overrides
        self._apply_theme_all()

    # ══════════════════════════════════════════════════════════════
    # Status
    # ══════════════════════════════════════════════════════════════
    def set_status(self, text: str, color=None):
        self.toolbar.set_status(text, color)

    # ══════════════════════════════════════════════════════════════
    # Image Upload / Navigation
    # ══════════════════════════════════════════════════════════════
    def upload_images(self):
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
            ("All files", "*.*"),
        ]
        files = filedialog.askopenfilenames(title="Select Images",
                                             filetypes=filetypes)
        if files:
            for f in files:
                if f not in self.uploaded_images:
                    self.uploaded_images.append(f)
                    self.left.add_item(f, self._remove_image)
            self.left.update_counter(len(self.uploaded_images))
            self._update_display()
            self.set_status(f"{len(self.uploaded_images)} images loaded")

    def _remove_image(self, filepath, frame):
        if filepath in self.uploaded_images:
            self.uploaded_images.remove(filepath)
        frame.destroy()
        self.left.update_counter(len(self.uploaded_images))
        self._update_display()

    def prev_image(self):
        if self.uploaded_images:
            self.current_image_index = (
                (self.current_image_index - 1) % len(self.uploaded_images)
            )
            self._update_display()

    def next_image(self):
        if self.uploaded_images:
            self.current_image_index = (
                (self.current_image_index + 1) % len(self.uploaded_images)
            )
            self._update_display()

    def _update_display(self):
        if not self.uploaded_images:
            self.center.show_placeholder()
            return
        idx = self.current_image_index
        path = self.uploaded_images[idx]
        try:
            img = Image.open(path).copy()
            self.center.show_image(
                img, idx, len(self.uploaded_images),
                os.path.basename(path)
            )
        except Exception as e:
            print(f"Display error: {e}")

    def toggle_comparison(self):
        if self.center.compare_var.get():
            messagebox.showinfo("Compare", "Side-by-side comparison enabled!")

    # ══════════════════════════════════════════════════════════════
    # Save
    # ══════════════════════════════════════════════════════════════
    def choose_save_location(self):
        folder = filedialog.askdirectory(title="Select Save Location")
        if folder:
            self.save_path = folder
            short = folder if len(folder) < 35 else f"...{folder[-32:]}"
            self.left.path_display.config(text=short)

    def create_new_folder(self):
        folder = filedialog.askdirectory(title="Select Parent Directory")
        if folder:
            name = f"Enhanced_Images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            new = os.path.join(folder, name)
            try:
                os.makedirs(new)
                self.save_path = new
                self.left.path_display.config(text=f"📁 {name}")
                messagebox.showinfo("Success", f"Folder created:\n{new}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{e}")

    def save_images(self):
        if not self.save_path:
            messagebox.showwarning("Warning", "Please select a save location first!")
            return
        if not self.enhanced_images:
            messagebox.showwarning("Warning", "No enhanced images to save!")
            return
        saved = 0
        for idx, img in self.enhanced_images.items():
            try:
                fn = f"enhanced_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img.save(os.path.join(self.save_path, fn))
                saved += 1
            except Exception as e:
                print(f"Save error: {e}")
        messagebox.showinfo("Success", f"Saved {saved} images to:\n{self.save_path}")
        self.set_status(f"Saved {saved} images")

    # ══════════════════════════════════════════════════════════════
    # Enhancement
    # ══════════════════════════════════════════════════════════════
    def enhance_images(self):
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Please upload images first!")
            return
        self.right.progress.config(text="Enhancing... Please wait")
        self.set_status("Processing...", self._current_theme()["warning"])
        self.right.enhance_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._enhance_thread, daemon=True).start()

    def _enhance_thread(self):
        model_key = self.selected_model.get()
        _name, enhance_fn = MODELS.get(model_key, MODELS["A"])
        for i, path in enumerate(self.uploaded_images):
            try:
                img = Image.open(path)
                self.enhanced_images[i] = enhance_fn(img)
                self.after(0, lambda c=i + 1: self.right.progress.config(
                    text=f"Enhanced {c}/{len(self.uploaded_images)} images"
                ))
            except Exception as e:
                print(f"Enhance error: {e}")
        self.after(0, self._enhance_done)

    def _enhance_done(self):
        self.right.progress.config(text="Enhancement complete! ✨")
        self.right.enhance_btn.config(state=tk.NORMAL)
        self._update_display()
        self.set_status("Ready")
        messagebox.showinfo("Success", "Images enhanced successfully!")

    # ══════════════════════════════════════════════════════════════
    # Tool Dialogs
    # ══════════════════════════════════════════════════════════════
    def open_resizing(self):
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Upload images first!")
            return
        dialogs.open_resize_dialog(self)

    def open_cropping(self):
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Upload images first!")
            return
        dialogs.open_crop_dialog(self)

    def open_augmentation(self):
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Upload images first!")
            return
        dialogs.open_augmentation_dialog(self)
