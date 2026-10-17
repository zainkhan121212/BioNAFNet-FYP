"""
left_panel.py — Neumorphic Upload, Model, Enhance, Save
=========================================================
Soft extruded cards, inset input fields, purple pill enhance button.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import theme as T
from neumorphic import neu_card, neu_inset, neu_button, neu_entry, hover_glow


class LeftPanel:
    WIDTH = 310

    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg=T.BG, width=self.WIDTH)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)
        self.frame.pack_propagate(False)
        self._build()

    def _build(self):
        scroll = tk.Frame(self.frame, bg=T.BG)
        scroll.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self._scroll = scroll

        # ═══════════════════ UPLOAD CARD ═══════════════════
        self.upload_outer, upload = neu_card(scroll, fill=tk.X, pady=(0, 10))
        upad = tk.Frame(upload, bg=T.BG)
        upad.pack(fill=tk.X, padx=16, pady=14)
        self._upad = upad

        hdr = tk.Frame(upad, bg=T.BG)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="📤", font=("Segoe UI", 12), bg=T.BG,
                 fg=T.TEXT2).pack(side=tk.LEFT)
        tk.Label(hdr, text="  Image Upload", font=T.FONT_HEADING,
                 bg=T.BG, fg=T.TEXT).pack(side=tk.LEFT)
        self.count_badge = tk.Label(hdr, text="0", font=T.FONT_TINY,
                                     bg=T.PURPLE_DIM, fg=T.TEXT, padx=8, pady=1)
        self.count_badge.pack(side=tk.RIGHT)

        # Drop zone (inset neumorphic)
        dz_outer, dz_surface = neu_inset(upad, fill=tk.X, pady=(10, 0))
        self._dz_outer = dz_outer
        dz_inner = tk.Frame(dz_surface, bg=T.INSET_BG, cursor="hand2")
        dz_inner.pack(padx=12, pady=14)
        tk.Label(dz_inner, text="🖼️", font=("Segoe UI", 22),
                 bg=T.INSET_BG, fg=T.TEXT3).pack()
        tk.Label(dz_inner, text="Click to upload images", font=T.FONT_SMALL,
                 bg=T.INSET_BG, fg=T.TEXT).pack(pady=3)
        tk.Label(dz_inner, text="PNG, JPG, WEBP", font=T.FONT_TINY,
                 bg=T.INSET_BG, fg=T.TEXT3).pack()
        dz_surface.bind("<Button-1>", lambda e: self.app.upload_images())
        for w in dz_inner.winfo_children():
            w.bind("<Button-1>", lambda e: self.app.upload_images())
        dz_inner.bind("<Button-1>", lambda e: self.app.upload_images())

        # Image list
        self.img_list = tk.Frame(upad, bg=T.BG)
        self.img_list.pack(fill=tk.X, pady=(6, 0))

        # ═══════════════════ MODEL CARD ═══════════════════
        self.model_outer, model = neu_card(scroll, fill=tk.X, pady=(0, 10))
        mpad = tk.Frame(model, bg=T.BG)
        mpad.pack(fill=tk.X, padx=16, pady=14)
        self._mpad = mpad

        mhdr = tk.Frame(mpad, bg=T.BG)
        mhdr.pack(fill=tk.X)
        tk.Label(mhdr, text="✨", font=("Segoe UI", 12), bg=T.BG,
                 fg=T.TEXT2).pack(side=tk.LEFT)
        tk.Label(mhdr, text="  Enhancement Model", font=T.FONT_HEADING,
                 bg=T.BG, fg=T.TEXT).pack(side=tk.LEFT)

        # Model dropdown (inset style)
        dd_outer, dd_surface = neu_inset(mpad, fill=tk.X, pady=(10, 0))
        self._dd_outer = dd_outer
        self.model_drop_btn = tk.Label(
            dd_surface, text="  ⚡  [A] Zero-DCE", font=T.FONT_BODY,
            bg=T.INSET_BG, fg=T.TEXT, cursor="hand2", anchor=tk.W,
            padx=12, pady=10
        )
        self.model_drop_btn.pack(fill=tk.X)
        self.model_drop_btn.bind("<Button-1>", lambda e: self._toggle_dropdown())

        # Dropdown list (hidden)
        self.dropdown = tk.Frame(mpad, bg=T.BG_DEEP)
        self._dropdown_visible = False
        self.model_btns = {}
        for m in T.MODELS:
            btn = tk.Label(
                self.dropdown,
                text=f"  {m['icon']}  [{m['id']}] {m['name']}",
                font=T.FONT_SMALL, bg=T.BG_DEEP, fg=T.TEXT2,
                cursor="hand2", anchor=tk.W, padx=12, pady=6
            )
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e, mid=m["id"]: self._select_model(mid))
            hover_glow(btn, T.BG_DEEP, T.BG_LIGHT, T.TEXT2, T.TEXT)
            self.model_btns[m["id"]] = btn

        # ENHANCE button (purple accent pill)
        self.enhance_btn = neu_button(
            mpad, "ENHANCE", command=self.app.enhance_images,
            accent=True, icon="✦"
        )
        self.enhance_btn.pack(fill=tk.X, pady=(12, 0))

        self.progress_lbl = tk.Label(mpad, text="", font=T.FONT_TINY,
                                      bg=T.BG, fg=T.TEXT3)
        self.progress_lbl.pack(fill=tk.X, pady=(4, 0))

        # ═══════════════════ SAVE CARD ═══════════════════
        self.save_outer, save = neu_card(scroll, fill=tk.X, pady=(0, 4))
        spad = tk.Frame(save, bg=T.BG)
        spad.pack(fill=tk.X, padx=16, pady=14)
        self._spad = spad

        shdr = tk.Frame(spad, bg=T.BG)
        shdr.pack(fill=tk.X)
        tk.Label(shdr, text="📂", font=("Segoe UI", 12), bg=T.BG,
                 fg=T.TEXT2).pack(side=tk.LEFT)
        tk.Label(shdr, text="  Output Settings", font=T.FONT_HEADING,
                 bg=T.BG, fg=T.TEXT).pack(side=tk.LEFT)

        # Save path (inset entry)
        tk.Label(spad, text="Save Path", font=T.FONT_TINY, bg=T.BG,
                 fg=T.TEXT3, anchor=tk.W).pack(fill=tk.X, pady=(10, 2))
        prow = tk.Frame(spad, bg=T.BG)
        prow.pack(fill=tk.X)
        path_outer, self.path_entry = neu_entry(prow, width=20)
        path_outer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.path_entry.insert(0, "C:/Users/enhanced")
        browse_btn = tk.Label(prow, text="💾", font=("Segoe UI", 12), bg=T.BG,
                               fg=T.TEXT2, cursor="hand2", padx=6)
        browse_btn.pack(side=tk.RIGHT, padx=(4, 0))
        browse_btn.bind("<Button-1>", lambda e: self.app.choose_save_location())

        # Folder name
        tk.Label(spad, text="New Folder", font=T.FONT_TINY, bg=T.BG,
                 fg=T.TEXT3, anchor=tk.W).pack(fill=tk.X, pady=(8, 2))
        frow = tk.Frame(spad, bg=T.BG)
        frow.pack(fill=tk.X)
        folder_outer, self.folder_entry = neu_entry(frow, width=20)
        folder_outer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.folder_entry.insert(0, "enhanced_output")
        folder_btn = tk.Label(frow, text="📁", font=("Segoe UI", 12), bg=T.BG,
                               fg=T.TEXT2, cursor="hand2", padx=6)
        folder_btn.pack(side=tk.RIGHT, padx=(4, 0))
        folder_btn.bind("<Button-1>", lambda e: self.app.create_new_folder())

        # Save button (standard neumorphic)
        self.save_btn = neu_button(spad, "Save Results", icon="💾")
        self.save_btn.pack(fill=tk.X, pady=(12, 0))
        # Bind save
        for child in self.save_btn.winfo_children():
            for sub in child.winfo_children():
                for w in sub.winfo_children():
                    w.bind("<Button-1>", lambda e: self.app.save_images())

    # ── Dropdown logic ─────────────────────────────────────
    def _toggle_dropdown(self):
        if self._dropdown_visible:
            self.dropdown.pack_forget()
        else:
            self.dropdown.pack(fill=tk.X, pady=(2, 0))
        self._dropdown_visible = not self._dropdown_visible

    def _select_model(self, mid):
        self.app.selected_model.set(mid)
        m = next((m for m in T.MODELS if m["id"] == mid), T.MODELS[0])
        self.model_drop_btn.config(text=f"  {m['icon']}  [{m['id']}] {m['name']}")
        self.dropdown.pack_forget()
        self._dropdown_visible = False
        self.app.set_status(f"Model {mid}: {m['name']}")

    def update_counter(self, n):
        self.count_badge.config(text=str(n))

    def add_item(self, filepath, remove_cb):
        fname = os.path.basename(filepath)
        short = fname if len(fname) <= 22 else fname[:19] + "..."
        row = tk.Frame(self.img_list, bg=T.BG_LIGHT)
        row.pack(fill=tk.X, pady=1)
        tk.Label(row, text=f"📷 {short}", font=T.FONT_TINY, bg=T.BG_LIGHT,
                 fg=T.TEXT, anchor=tk.W).pack(side=tk.LEFT, padx=8, pady=3)
        x_btn = tk.Label(row, text="✕", font=("Segoe UI", 9), bg=T.BG_LIGHT,
                          fg=T.RED, cursor="hand2")
        x_btn.pack(side=tk.RIGHT, padx=6)
        x_btn.bind("<Button-1>", lambda e: remove_cb(filepath, row))

    def apply_theme(self):
        gpu = self.app.gpu_enabled.get()
        # Set outer glow using the new set_glow method on NeuWidget
        self.upload_outer.set_glow(gpu, T.PURPLE)
        self.model_outer.set_glow(gpu, T.PURPLE)
        self.save_outer.set_glow(gpu, T.PURPLE)
