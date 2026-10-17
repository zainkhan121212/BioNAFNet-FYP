"""
app.py — PixelForge with Dark Neumorphism Design
===================================================
Same functionality, new soft UI visual system.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime
from PIL import Image

try:
    import pywinstyles
    HAS_PYWINSTYLES = True
except ImportError:
    HAS_PYWINSTYLES = False

import theme as T
from components.header import Header
from components.left_panel import LeftPanel
from components.center_panel import CenterPanel
from components.right_panel import RightPanel
from components.status_bar import StatusBar
from animations.particles import ParticleSystem
from animations.scan_line import ScanLine
from animations.effects import GlowEngine


class PixelForgeApp:
    """Main PixelForge application — Dark Neumorphism edition."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PixelForge — AI Image Enhancement Studio")
        self.root.geometry("1440x900")
        self.root.minsize(1200, 750)
        self.root.config(bg=T.BG)

        # ── State ──────────────────────────────────────────────────
        self.dark_mode       = tk.BooleanVar(value=True)
        self.gpu_enabled     = tk.BooleanVar(value=False)
        self.selected_model  = tk.StringVar(value="A")
        self.uploaded_images: list[str] = []
        self.current_image_index = 0
        self.enhanced_images: dict[int, Image.Image] = {}
        self.save_path       = ""

        # ── Build UI ───────────────────────────────────────────────
        self._build_ui()

        # ── Animations ─────────────────────────────────────────────
        self.glow = GlowEngine(self.root)
        self.particles = ParticleSystem(self.bg_canvas)
        self.scan_line = ScanLine(self.bg_canvas)

        self.glow.register_logo(self.header.logo_icon)
        self.glow.register_gpu_dot(self.status.gpu_dot)
        self.glow.start()

        # ── Windows dark title bar ─────────────────────────────────
        if HAS_PYWINSTYLES and sys.platform == "win32":
            try:
                pywinstyles.apply_style(self.root, "dark")
                self.root.update_idletasks()
            except Exception:
                pass

    def run(self):
        self.root.mainloop()

    # ════════════════════════════════════════════════════════════════
    # Layout
    # ════════════════════════════════════════════════════════════════
    def _build_ui(self):
        # Root frame
        self.root_frame = tk.Frame(self.root, bg=T.BG)
        self.root_frame.pack(fill=tk.BOTH, expand=True)

        # Background canvas for particles
        self.bg_canvas = tk.Canvas(self.root_frame, bg=T.BG, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Header
        self.header = Header(self.root_frame, self)
        self.header.frame.lift()

        # Content row
        self.content = tk.Frame(self.root_frame, bg=T.BG)
        self.content.pack(fill=tk.BOTH, expand=True)
        self.content.lift()

        self.left   = LeftPanel(self.content, self)
        self.right  = RightPanel(self.content, self)
        self.center = CenterPanel(self.content, self)

        # Status bar
        self.status = StatusBar(self.root_frame, self)
        self.status.frame.lift()

    # ════════════════════════════════════════════════════════════════
    # Theme
    # ════════════════════════════════════════════════════════════════
    def toggle_theme(self):
        # Neumorphic design looks best in dark, but toggle icon
        self.dark_mode.set(not self.dark_mode.get())
        self._apply_theme_all()

    def _apply_theme_all(self):
        self.header.apply_theme()
        self.left.apply_theme()
        self.center.apply_theme()
        self.right.apply_theme()
        self.status.apply_theme()

    # ════════════════════════════════════════════════════════════════
    # GPU Toggle
    # ════════════════════════════════════════════════════════════════
    def toggle_gpu(self):
        self.gpu_enabled.set(not self.gpu_enabled.get())
        if self.gpu_enabled.get():
            self.particles.start()
            self.scan_line.start()
            self.glow.set_gpu(True)
            self.set_status("GPU Accelerated")
        else:
            self.particles.stop()
            self.scan_line.stop()
            self.glow.set_gpu(False)
            self.set_status("Ready")
        self._apply_theme_all()

    # ════════════════════════════════════════════════════════════════
    # Status
    # ════════════════════════════════════════════════════════════════
    def set_status(self, text):
        self.status.set_status(text)

    # ════════════════════════════════════════════════════════════════
    # Upload / Navigation
    # ════════════════════════════════════════════════════════════════
    def upload_images(self):
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp"),
            ("All files", "*.*"),
        ]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        if files:
            for f in files:
                if f not in self.uploaded_images:
                    self.uploaded_images.append(f)
                    self.left.add_item(f, self._remove_image)
            self.left.update_counter(len(self.uploaded_images))
            self.status.update_count(len(self.uploaded_images))
            self._update_display()
            self.set_status(f"{len(self.uploaded_images)} images loaded")

    def _remove_image(self, filepath, frame):
        if filepath in self.uploaded_images:
            self.uploaded_images.remove(filepath)
        frame.destroy()
        self.left.update_counter(len(self.uploaded_images))
        self.status.update_count(len(self.uploaded_images))
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
                img, idx, len(self.uploaded_images), os.path.basename(path)
            )
        except Exception as e:
            print(f"Display error: {e}")

    def toggle_comparison(self):
        pass

    # ════════════════════════════════════════════════════════════════
    # Save
    # ════════════════════════════════════════════════════════════════
    def choose_save_location(self):
        folder = filedialog.askdirectory(title="Select Save Location")
        if folder:
            self.save_path = folder
            self.left.path_entry.delete(0, tk.END)
            self.left.path_entry.insert(0, folder)

    def create_new_folder(self):
        folder = filedialog.askdirectory(title="Select Parent Directory")
        if folder:
            name = self.left.folder_entry.get() or "enhanced_output"
            new = os.path.join(folder, name)
            try:
                os.makedirs(new)
                self.save_path = new
                self.left.path_entry.delete(0, tk.END)
                self.left.path_entry.insert(0, new)
                messagebox.showinfo("Success", f"Folder created:\n{new}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_images(self):
        sp = self.save_path or self.left.path_entry.get()
        if not sp:
            messagebox.showwarning("Warning", "No save path set!")
            return
        if not self.enhanced_images:
            messagebox.showwarning("Warning", "No enhanced images!")
            return
        saved = 0
        for idx, img in self.enhanced_images.items():
            try:
                fn = f"enhanced_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img.save(os.path.join(sp, fn))
                saved += 1
            except Exception as e:
                print(f"Save error: {e}")
        messagebox.showinfo("Saved", f"{saved} images saved to:\n{sp}")

    # ════════════════════════════════════════════════════════════════
    # Enhancement
    # ════════════════════════════════════════════════════════════════
    def enhance_images(self):
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Upload images first!")
            return
        # Find the enhance label inside the neu_button
        for child in self.enhance_btn_children():
            try:
                child.config(fg=T.TEXT3)
            except:
                pass
        self.left.progress_lbl.config(text="Enhancing... please wait")
        self.set_status("Processing...")
        threading.Thread(target=self._enhance_thread, daemon=True).start()

    def enhance_btn_children(self):
        """Get labels inside the enhance button."""
        try:
            return [self.left.enhance_btn]
        except:
            return []

    def _enhance_thread(self):
        from utils.image_processing import MODELS as PROC_MODELS
        model_key = self.selected_model.get()
        _name, fn = PROC_MODELS.get(model_key, list(PROC_MODELS.values())[0])
        for i, path in enumerate(self.uploaded_images):
            try:
                img = Image.open(path)
                self.enhanced_images[i] = fn(img)
                self.root.after(0, lambda c=i + 1: self.left.progress_lbl.config(
                    text=f"Enhanced {c}/{len(self.uploaded_images)}"
                ))
            except Exception as e:
                print(f"Enhance error: {e}")
        self.root.after(0, self._enhance_done)

    def _enhance_done(self):
        self.left.progress_lbl.config(text="Enhancement complete! ✨")
        self._update_display()
        self.set_status("Ready")
        messagebox.showinfo("Success", "Images enhanced!")
