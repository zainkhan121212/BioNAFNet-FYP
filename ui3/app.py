"""
app.py — Main Application with Sidebar Routing
=================================================
Only one page is visible at a time; sidebar switches between them.
"""

import sys
import os
import customtkinter as ctk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import theme as T
from widgets.sidebar import Sidebar
from pages.enhance import EnhancePage
from pages.augmentation import AugmentationPage
from pages.cropping import CroppingPage
from pages.resizing import ResizingPage
from pages.live_preview import LivePreviewPage


class PixelForgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ── Window Setup ───────────────────────────────────────
        self.title("PixelForge — AI Image Enhancement Studio")
        self.geometry("1440x900")
        self.minsize(1200, 750)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.configure(fg_color=T.BG_DARK)

        # ── Sidebar ────────────────────────────────────────────
        self.sidebar = Sidebar(self, on_navigate=self._navigate)

        # ── Page Container ─────────────────────────────────────
        self.container = ctk.CTkFrame(self, fg_color=T.BG_MAIN, corner_radius=0)
        self.container.pack(side="left", fill="both", expand=True)

        # ── Create Pages ───────────────────────────────────────
        self.pages: dict[str, ctk.CTkFrame] = {}
        for PageClass, key in [
            (EnhancePage,       "enhance"),
            (AugmentationPage,  "augmentation"),
            (ResizingPage,      "resizing"),
            (CroppingPage,      "cropping"),
            (LivePreviewPage,   "live_preview"),
        ]:
            page = PageClass(self.container)
            self.pages[key] = page

        # ── Show Default Page ──────────────────────────────────
        self._current_key = ""
        self._navigate("enhance")

    def _navigate(self, key: str):
        if key == self._current_key:
            return

        # Hide current
        if self._current_key and self._current_key in self.pages:
            self.pages[self._current_key].pack_forget()

        # Show new
        self.pages[key].pack(fill="both", expand=True)
        self._current_key = key

        # Update sidebar indicators
        self.sidebar.set_active(key)
