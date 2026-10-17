"""
sidebar.py — Animated Futuristic Sidebar Navigation
=====================================================
Persistent sidebar with 5 page buttons, glow indicator, and slide animation.
"""

import customtkinter as ctk
import theme as T


class SidebarButton(ctk.CTkFrame):
    """A single nav button with hover glow and active indicator."""

    def __init__(self, parent, icon, label, key, command, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=12, **kwargs)
        self.key = key
        self._command = command
        self._active = False

        # Indicator bar (left edge)
        self.indicator = ctk.CTkFrame(self, width=4, height=36,
                                       corner_radius=2, fg_color="transparent")
        self.indicator.pack(side="left", padx=(0, 8), pady=8)

        # Icon
        self.icon_lbl = ctk.CTkLabel(self, text=icon, font=T.FONT_ICON,
                                      text_color=T.TEXT_DIM)
        self.icon_lbl.pack(side="left", padx=(4, 8))

        # Label
        self.label_lbl = ctk.CTkLabel(self, text=label, font=T.FONT_NAV,
                                       text_color=T.TEXT_DIM, anchor="w")
        self.label_lbl.pack(side="left", fill="x", expand=True)

        # Bind clicks
        for w in (self, self.icon_lbl, self.label_lbl):
            w.bind("<Button-1>", lambda e: self._on_click())
            w.bind("<Enter>", lambda e: self._on_enter())
            w.bind("<Leave>", lambda e: self._on_leave())
        self.configure(cursor="hand2")

    def _on_click(self):
        self._command(self.key)

    def _on_enter(self):
        if not self._active:
            self.configure(fg_color=T.BG_HOVER)
            self.icon_lbl.configure(text_color=T.TEXT)
            self.label_lbl.configure(text_color=T.TEXT)

    def _on_leave(self):
        if not self._active:
            self.configure(fg_color="transparent")
            self.icon_lbl.configure(text_color=T.TEXT_DIM)
            self.label_lbl.configure(text_color=T.TEXT_DIM)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.configure(fg_color=T.BG_HOVER)
            self.indicator.configure(fg_color=T.ACCENT)
            self.icon_lbl.configure(text_color=T.ACCENT)
            self.label_lbl.configure(text_color=T.TEXT, font=T.FONT_NAV_BOLD)
        else:
            self.configure(fg_color="transparent")
            self.indicator.configure(fg_color="transparent")
            self.icon_lbl.configure(text_color=T.TEXT_DIM)
            self.label_lbl.configure(text_color=T.TEXT_DIM, font=T.FONT_NAV)


class Sidebar(ctk.CTkFrame):
    """Persistent sidebar with logo + page buttons + footer."""

    WIDTH = 220

    def __init__(self, parent, on_navigate):
        super().__init__(parent, width=self.WIDTH, corner_radius=0,
                         fg_color=T.BG_SIDEBAR)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._buttons: dict[str, SidebarButton] = {}
        self._build()

    def _build(self):
        # ── Logo ───────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(20, 6))

        ctk.CTkLabel(logo_frame, text="⬡", font=("Segoe UI", 32),
                     text_color=T.ACCENT).pack(side="left", padx=(0, 10))
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text="PixelForge", font=(T.FONT_FAMILY, 18, "bold"),
                     text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="AI Enhancement", font=T.FONT_TINY,
                     text_color=T.TEXT_MUTED).pack(anchor="w")

        # Accent line
        ctk.CTkFrame(self, height=2, fg_color=T.ACCENT, corner_radius=1).pack(
            fill="x", padx=20, pady=(10, 16))

        # Section label
        ctk.CTkLabel(self, text="  MODULES", font=(T.FONT_FAMILY, 10, "bold"),
                     text_color=T.TEXT_MUTED, anchor="w").pack(
            fill="x", padx=20, pady=(0, 6))

        # ── Nav Buttons ────────────────────────────────────────
        for page in T.PAGES:
            btn = SidebarButton(self, page["icon"], page["label"],
                                page["key"], self._navigate)
            btn.pack(fill="x", padx=10, pady=2)
            self._buttons[page["key"]] = btn

        # ── Footer ─────────────────────────────────────────────
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkFrame(self, height=1, fg_color=T.BORDER).pack(fill="x", padx=20, pady=(0, 10))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(0, 16))
        self.status_dot = ctk.CTkLabel(footer, text="●", font=("Segoe UI", 10),
                                        text_color=T.ACCENT_GREEN)
        self.status_dot.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(footer, text="System Ready", font=T.FONT_TINY,
                     text_color=T.TEXT_MUTED).pack(side="left")

        ver_lbl = ctk.CTkLabel(self, text="v3.0.0", font=T.FONT_TINY,
                                text_color=T.TEXT_DARK)
        ver_lbl.pack(pady=(0, 10))

    def _navigate(self, key):
        self._on_navigate(key)

    def set_active(self, key):
        for k, btn in self._buttons.items():
            btn.set_active(k == key)
