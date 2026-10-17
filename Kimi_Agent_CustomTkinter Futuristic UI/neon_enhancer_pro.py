#!/usr/bin/env python3
"""
NeonEnhancer Pro - Futuristic Image Processing Suite
A highly creative, futuristic desktop application built with customtkinter
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import os
import math
import threading
from datetime import datetime

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import model_hooks

# Maximum images selectable per page (enhance, augment, crop, resize)
MAX_PAGE_IMAGES = 50

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class NeonEnhancerPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(" LOL IMAGE ENHANCER")
        self.geometry("1600x1000")
        self.minsize(1400, 900)
        # from the linbe of  1686 function
        # Futuristic color palette
        self.colors = {
            'bg_dark': '#0a0a0f',
            'bg_card': '#12121a',
            'bg_hover': '#1a1a25',
            'neon_cyan': '#00f5ff',
            'neon_purple': '#b829dd',
            'neon_pink': '#ff006e',
            'neon_blue': '#3a86ff',
            'neon_green': '#06ffa5',
            'text_primary': '#ffffff',
            'text_secondary': '#8b8b9a',
            'border': '#2a2a3a',
            'accent': '#6366f1'
        }
        
        # Configure main window
        self.configure(fg_color=self.colors['bg_dark'])
        
        self.current_page = None
        
        # Data storage
        self.uploaded_images = []
        self.current_image = None
        self.enhanced_image = None
        self.save_directory = ""
        self.processing_mode = "CPU"
        self.ground_truth_images = []           # list of GT paths (one per input)
        
        # Batch gallery state
        self.batch_results = []                 # list of (orig_path, enhanced_PIL)
        self.gallery_index = 0                  # current page in gallery
        self._gallery_refs = []                 # prevent GC of CTkImage objects
        
        # Crop / resize multi-image preview index
        self.crop_preview_index = 0
        self.resize_preview_index = 0
        
        # Create UI
        self.create_main_layout()
        self.create_sidebar()
        self.create_content_area()
        self.create_pages()
        
        # Show default page
        self.show_page("enhance")
        
    def _check_image_count(self, n: int) -> bool:
        """Return False and show an error if more than MAX_PAGE_IMAGES were selected."""
        if n > MAX_PAGE_IMAGES:
            messagebox.showerror(
                "Too many images",
                f"You can select at most {MAX_PAGE_IMAGES} images on this page.\n"
                f"You selected {n}. Please choose fewer images and try again."
            )
            return False
        return True
        
    def create_main_layout(self):
        """Create the main application layout"""
        # Main container
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg_dark'],
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
    def create_sidebar(self):
        """Create sidebar navigation"""
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            width=280,
            fg_color=self.colors['bg_card'],
            corner_radius=0,
            border_width=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo section
        self.logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=100
        )
        self.logo_frame.pack(fill="x", padx=20, pady=30)
        
        self.logo_icon = ctk.CTkLabel(
            self.logo_frame,
            text="◈",
            font=("Orbitron", 48, "bold"),
            text_color=self.colors['neon_cyan']
        )
        self.logo_icon.pack()
        
        # Logo text
        self.logo_text = ctk.CTkLabel(
            self.logo_frame,
            text="LOL IMAGE ENHANCER",
            font=("Orbitron", 16, "bold"),
            text_color=self.colors['text_primary'],
            justify="center"
        )
        self.logo_text.pack(pady=(5, 0))
        
        # Version badge
        self.version_badge = ctk.CTkLabel(
            self.logo_frame,
            text="v3.0",
            font=("Rajdhani", 10),
            text_color=self.colors['neon_purple'],
            fg_color=self.colors['bg_dark'],
            corner_radius=10,
            width=50
        )
        self.version_badge.pack(pady=5)
        
        # Navigation buttons container
        self.nav_container = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.nav_container.pack(fill="x", padx=15, pady=20)
        
        # Navigation items
        self.nav_items = [
            ("enhance", "✨", "Enhance", self.colors['neon_cyan']),
            ("augmentation", "🔄", "Augmentation", self.colors['neon_purple']),
            ("cropping", "✂️", "Cropping", self.colors['neon_pink']),
            ("resizing", "📐", "Resizing", self.colors['neon_blue']),
            ("live", "📹", "Live Preview", self.colors['neon_green'])
        ]
        
        self.nav_buttons = {}
        for page_id, icon, text, color in self.nav_items:
            btn = self.create_nav_button(page_id, icon, text, color)
            btn.pack(fill="x", pady=5)
            self.nav_buttons[page_id] = btn
            
        # Bottom section - Hardware status
        self.hardware_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors['bg_dark'],
            corner_radius=15,
            height=80
        )
        self.hardware_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        self.hardware_frame.pack_propagate(False)
        
        self.hardware_label = ctk.CTkLabel(
            self.hardware_frame,
            text="⚡ HARDWARE",
            font=("Rajdhani", 12, "bold"),
            text_color=self.colors['text_secondary']
        )
        self.hardware_label.pack(pady=(10, 5))
        
        self.hardware_status = ctk.CTkLabel(
            self.hardware_frame,
            text="CPU MODE ACTIVE",
            font=("Rajdhani", 11),
            text_color=self.colors['neon_green']
        )
        self.hardware_status.pack()
        
    def create_nav_button(self, page_id, icon, text, accent_color):
        """Create a futuristic navigation button"""
        btn_frame = ctk.CTkFrame(
            self.nav_container,
            fg_color="transparent",
            height=55,
            corner_radius=12
        )
        
        # Button content
        content = ctk.CTkFrame(btn_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=("Segoe UI", 18),
            width=30
        )
        icon_label.pack(side="left")
        
        # Text
        text_label = ctk.CTkLabel(
            content,
            text=text,
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['text_primary']
        )
        text_label.pack(side="left", padx=(15, 0))
        
        # Active indicator (hidden by default)
        indicator = ctk.CTkFrame(
            btn_frame,
            width=4,
            height=40,
            fg_color=accent_color,
            corner_radius=2
        )
        indicator.place(relx=0, rely=0.5, anchor="w")
        indicator.place_forget()
        
        # Store references
        btn_frame.icon_label = icon_label
        btn_frame.text_label = text_label
        btn_frame.indicator = indicator
        btn_frame.accent_color = accent_color
        btn_frame.page_id = page_id
        
        # Bind click event
        btn_frame.bind("<Button-1>", lambda e, p=page_id: self.show_page(p))
        for child in btn_frame.winfo_children():
            child.bind("<Button-1>", lambda e, p=page_id: self.show_page(p))
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", lambda e, p=page_id: self.show_page(p))
        
        # Hover effects
        btn_frame.bind("<Enter>", lambda e, b=btn_frame: self.on_nav_hover(b, True))
        btn_frame.bind("<Leave>", lambda e, b=btn_frame: self.on_nav_hover(b, False))
        
        return btn_frame
        
    def on_nav_hover(self, btn_frame, entering):
        """Handle navigation button hover"""
        if entering:
            btn_frame.configure(fg_color=self.colors['bg_hover'])
            btn_frame.icon_label.configure(text_color=btn_frame.accent_color)
        else:
            if self.current_page != btn_frame.page_id:
                btn_frame.configure(fg_color="transparent")
                btn_frame.icon_label.configure(text_color=self.colors['text_primary'])
                
    def create_content_area(self):
        """Create the main content area"""
        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.colors['bg_dark'],
            corner_radius=0
        )
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        ### thsi si where we have to create the pages for our app
    def create_pages(self):
        """Create all 5 pages"""
        self.pages = {}
        
        # Create each page
        self.pages['enhance'] = self.create_enhance_page()
        self.pages['augmentation'] = self.create_augmentation_page()
        self.pages['cropping'] = self.create_cropping_page()
        self.pages['resizing'] = self.create_resizing_page()
        self.pages['live'] = self.create_live_page()
        #tghis is where wee made our enhaced pages and widget s are cominmng fro mhere
    def create_enhance_page(self):
        """Create the Enhance page with model selection and comparison"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(page, fg_color="transparent", height=60)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="✨ IMAGE ENHANCEMENT",
            font=("Orbitron", 24, "bold"),
            text_color=self.colors['text_primary']
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            header,
            text="AI-powered low-light image enhancement",
            font=("Rajdhani", 14),
            text_color=self.colors['text_secondary']
        )
        subtitle.pack(side="left", padx=(20, 0))
        
        # Main content split — controls get 1 part, gallery gets 2 parts
        main_split = ctk.CTkFrame(page, fg_color="transparent")
        main_split.pack(fill="both", expand=True)
        main_split.grid_columnconfigure(0, weight=1)   # controls (narrow)
        main_split.grid_columnconfigure(1, weight=2)   # gallery  (wide)
        main_split.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls
        left_panel = ctk.CTkFrame(
            main_split,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # I/O Section
        io_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        io_section.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            io_section,
            text="📁 INPUT / OUTPUT",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_cyan']
        ).pack(anchor="w")
        
        # Upload button
        self.enhance_upload_btn = ctk.CTkButton(
            io_section,
            text="⬆ Upload Image(s)",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.upload_enhance_images
        )
        self.enhance_upload_btn.pack(fill="x", pady=(15, 5))

        # NEW: Upload Folder button — scans selected folder for all images
        self.enhance_upload_folder_btn = ctk.CTkButton(
            io_section,
            text="📂 Upload Folder",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_green'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.upload_enhance_folder
        )
        self.enhance_upload_folder_btn.pack(fill="x", pady=(0, 10))
        
        # Save directory button
        self.enhance_save_btn = ctk.CTkButton(
            io_section,
            text="💾 Select Save Directory",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.select_save_directory
        )
        self.enhance_save_btn.pack(fill="x", pady=5)
        
        # Selected path display
        self.save_path_label = ctk.CTkLabel(
            io_section,
            text="No directory selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary'],
            wraplength=300
        )
        self.save_path_label.pack(anchor="w", pady=(10, 0))
        
        # Separator
        ctk.CTkFrame(left_panel, height=1, fg_color=self.colors['border']).pack(fill="x", padx=20, pady=10)
        
        # Model Selection
        model_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        model_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            model_section,
            text="🤖 MODEL SELECTION",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_purple']
        ).pack(anchor="w")
        
        # Model dropdown (options mirror model_hooks.UNSUPERVISED_MODELS)
        _unsup_names = list(model_hooks.UNSUPERVISED_MODELS.keys())
        _default_model = _unsup_names[0] if _unsup_names else "Zero-DCE"
        self.model_var = ctk.StringVar(value=_default_model)
        self.model_dropdown = ctk.CTkOptionMenu(
            model_section,
            values=_unsup_names,
            variable=self.model_var,
            font=("Rajdhani", 13),
            dropdown_font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            button_color=self.colors['neon_purple'],
            button_hover_color=self.colors['neon_pink'],
            dropdown_fg_color=self.colors['bg_card'],
            dropdown_hover_color=self.colors['bg_hover'],
            dropdown_text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45
        )
        self.model_dropdown.pack(fill="x", pady=(15, 10))
        
        # Model description
        self.model_desc = ctk.CTkLabel(
            model_section,
            text="",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        self.model_desc.pack(anchor="w", pady=5)
        
        # Update description on model change
        self.model_dropdown.configure(command=self.update_model_description)
        self.update_model_description(_default_model)
        
        # Separator
        ctk.CTkFrame(left_panel, height=1, fg_color=self.colors['border']).pack(fill="x", padx=20, pady=10)
        
        # Hardware Toggle
        hardware_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        hardware_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            hardware_section,
            text="⚡ PROCESSING MODE",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_green']
        ).pack(anchor="w")
        
        # CPU/GPU Toggle
        toggle_frame = ctk.CTkFrame(hardware_section, fg_color="transparent")
        toggle_frame.pack(fill="x", pady=(15, 10))
        
        self.cpu_label = ctk.CTkLabel(
            toggle_frame,
            text="CPU",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_green']
        )
        self.cpu_label.pack(side="left")
        
        self.hardware_switch = ctk.CTkSwitch(
            toggle_frame,
            text="",
            width=60,
            height=30,
            switch_width=60,
            switch_height=30,
            fg_color=self.colors['border'],
            progress_color=self.colors['neon_cyan'],
            button_color=self.colors['text_primary'],
            button_hover_color=self.colors['neon_cyan'],
            command=self.toggle_hardware
        )
        self.hardware_switch.pack(side="left", padx=15)
        
        self.gpu_label = ctk.CTkLabel(
            toggle_frame,
            text="GPU",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['text_secondary']
        )
        self.gpu_label.pack(side="left")
        
        # PSNR / SSIM vs ground truth (only meaningful when GT paths are loaded)
        self.gt_metrics_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.gt_metrics_section.pack(fill="x", padx=20, pady=(4, 8))
        ctk.CTkLabel(
            self.gt_metrics_section,
            text="📊 VS GROUND TRUTH",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_cyan'],
        ).pack(anchor="w")
        _mfont = ("Segoe UI", 12)
        _mfont_small = ("Segoe UI", 11)
        self.metric_psnr_label = ctk.CTkLabel(
            self.gt_metrics_section,
            text="PSNR: —",
            font=_mfont,
            text_color=self.colors['text_primary'],
            anchor="w",
            justify="left",
            wraplength=300,
            width=300,
        )
        self.metric_psnr_label.pack(anchor="w", pady=(6, 2))
        self.metric_ssim_label = ctk.CTkLabel(
            self.gt_metrics_section,
            text="SSIM: —",
            font=_mfont,
            text_color=self.colors['text_primary'],
            anchor="w",
            justify="left",
            wraplength=300,
            width=300,
        )
        self.metric_ssim_label.pack(anchor="w", pady=(0, 2))
        self.metric_mean_label = ctk.CTkLabel(
            self.gt_metrics_section,
            text="",
            font=_mfont_small,
            text_color=self.colors['text_secondary'],
            justify="left",
            anchor="w",
            wraplength=300,
            width=300,
        )
        self.metric_mean_label.pack(anchor="w", pady=(2, 0))
        
        # Enhance button
        ctk.CTkFrame(left_panel, height=1, fg_color=self.colors['border']).pack(fill="x", padx=20, pady=10)
        
        self.enhance_btn = ctk.CTkButton(
            left_panel,
            text="✨ ENHANCE IMAGE",
            font=("Orbitron", 16, "bold"),
            fg_color=self.colors['neon_cyan'],
            hover_color=self.colors['neon_blue'],
            text_color=self.colors['bg_dark'],
            corner_radius=15,
            height=55,
            command=self.enhance_image
        )
        self.enhance_btn.pack(fill="x", padx=20, pady=(20, 10))
        
        # Clear / Reset button
        self.clear_btn = ctk.CTkButton(
            left_panel,
            text="🔄 CLEAR ALL",
            font=("Rajdhani", 14, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_pink'],
            text_color=self.colors['text_secondary'],
            corner_radius=12,
            height=40,
            command=self.clear_enhance_state
        )
        self.clear_btn.pack(fill="x", padx=20, pady=(0, 15))
        
        # Progress bar (hidden initially)
        self.progress_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=8,
            fg_color=self.colors['border'],
            progress_color=self.colors['neon_cyan'],
            corner_radius=4
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Processing... 0%",
            font=("Rajdhani", 11),
            text_color=self.colors['neon_cyan']
        )
        self.progress_label.pack(pady=5)
        
        # Right panel — Split-Screen Gallery Preview
        right_panel = ctk.CTkFrame(
            main_split,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Preview header
        comp_header = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        comp_header.pack(fill="x", padx=20, pady=15)
        comp_header.pack_propagate(False)
        
        ctk.CTkLabel(
            comp_header,
            text="👁️ GALLERY PREVIEW",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_pink']
        ).pack(side="left")
        
        # Page counter label
        self.gallery_counter = ctk.CTkLabel(
            comp_header,
            text="0 / 0",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_cyan']
        )
        self.gallery_counter.pack(side="right")
        
        # ── Split-screen image area ──
        self.preview_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.preview_container.pack(fill="both", expand=True, padx=20, pady=(0, 5))
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(1, weight=1)
        self.preview_container.grid_rowconfigure(1, weight=1)
        
        # Column labels
        ctk.CTkLabel(
            self.preview_container, text="ORIGINAL",
            font=("Orbitron", 11, "bold"),
            text_color=self.colors['text_secondary']
        ).grid(row=0, column=0, pady=(0, 5))
        ctk.CTkLabel(
            self.preview_container, text="ENHANCED",
            font=("Orbitron", 11, "bold"),
            text_color=self.colors['neon_cyan']
        ).grid(row=0, column=1, pady=(0, 5))
        
        # Left image (original) — native tk.Label for reliable PhotoImage display
        orig_frame = ctk.CTkFrame(
            self.preview_container,
            fg_color=self.colors['bg_dark'], corner_radius=12
        )
        orig_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        orig_frame.grid_rowconfigure(0, weight=1)
        orig_frame.grid_columnconfigure(0, weight=1)
        self.preview_orig_label = tk.Label(
            orig_frame,
            text="📷\n\nUpload images\nto see preview",
            bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
            font=("Rajdhani", 14), compound="center",
            anchor="center"
        )
        self.preview_orig_label.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # Right image (enhanced) — native tk.Label
        enh_frame = ctk.CTkFrame(
            self.preview_container,
            fg_color=self.colors['bg_dark'], corner_radius=12
        )
        enh_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        enh_frame.grid_rowconfigure(0, weight=1)
        enh_frame.grid_columnconfigure(0, weight=1)
        self.preview_enh_label = tk.Label(
            enh_frame,
            text="✨\n\nEnhanced result\nwill appear here",
            bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
            font=("Rajdhani", 14), compound="center",
            anchor="center"
        )
        self.preview_enh_label.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        
        # ── Navigation buttons ──
        nav_frame = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        nav_frame.pack(fill="x", padx=20, pady=(5, 15))
        nav_frame.pack_propagate(False)
        
        self.prev_btn = ctk.CTkButton(
            nav_frame, text="◀  Previous",
            font=("Rajdhani", 13, "bold"), width=120, height=36,
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12, command=self._gallery_prev
        )
        self.prev_btn.pack(side="left")
        
        self.gallery_filename = ctk.CTkLabel(
            nav_frame, text="",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.gallery_filename.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(
            nav_frame, text="Next  ▶",
            font=("Rajdhani", 13, "bold"), width=120, height=36,
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12, command=self._gallery_next
        )
        self.next_btn.pack(side="right")
        
        return page
        
    def create_augmentation_page(self):
        """Create the Augmentation page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(page, fg_color="transparent", height=60)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="🔄 DATA AUGMENTATION",
            font=("Orbitron", 24, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Generate multiple variations of your images",
            font=("Rajdhani", 14),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(20, 0))
        
        # Main content
        main_content = ctk.CTkFrame(page, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=2)
        main_content.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls
        left_panel = ctk.CTkFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Upload section
        upload_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        upload_section.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            upload_section,
            text="📁 UPLOAD IMAGES",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_cyan']
        ).pack(anchor="w")
        
        self.aug_upload_btn = ctk.CTkButton(
            upload_section,
            text="⬆ Upload Multiple Images",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.upload_augment_images
        )
        self.aug_upload_btn.pack(fill="x", pady=(15, 10))
        
        # Image count
        self.aug_count_label = ctk.CTkLabel(
            upload_section,
            text="0 images selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.aug_count_label.pack(anchor="w")
        
        # Save directory
        self.aug_save_btn = ctk.CTkButton(
            upload_section,
            text="💾 Select Save Folder",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.select_aug_save_directory
        )
        self.aug_save_btn.pack(fill="x", pady=(15, 10))
        
        self.aug_save_label = ctk.CTkLabel(
            upload_section,
            text="No folder selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.aug_save_label.pack(anchor="w")
        
        # Separator
        ctk.CTkFrame(left_panel, height=1, fg_color=self.colors['border']).pack(fill="x", padx=20, pady=15)
        
        # Info section describing new behavior
        info_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        info_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_section,
            text="🔄 ROTATION AUGMENTATION",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_purple']
        ).pack(anchor="w")
        
        info_text = (
            "Clicking Generate will automatically create\n"
            "3 new versions for each uploaded image:\n\n"
            "• Rotated 90°\n"
            "• Rotated 180°\n"
            "• Rotated 270°"
        )
        
        ctk.CTkLabel(
            info_section,
            text=info_text,
            font=("Rajdhani", 13),
            text_color=self.colors['text_secondary'],
            justify="left"
        ).pack(anchor="w", pady=(10, 15))
        
        # Generate button
        self.aug_generate_btn = ctk.CTkButton(
            left_panel,
            text="🔄 GENERATE AUGMENTED DATA",
            font=("Orbitron", 16, "bold"),
            fg_color=self.colors['neon_purple'],
            hover_color=self.colors['neon_pink'],
            text_color=self.colors['text_primary'],
            corner_radius=15,
            height=55,
            command=self.generate_augmented_data
        )
        self.aug_generate_btn.pack(fill="x", padx=20, pady=20)
        
        # (Preview panel removed per user request)
        
        return page
        
    def create_cropping_page(self):
        """Create the Cropping page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(page, fg_color="transparent", height=60)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="✂️ IMAGE CROPPING",
            font=("Orbitron", 24, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Precise pixel-level cropping control",
            font=("Rajdhani", 14),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(20, 0))
        
        # Main content
        main_content = ctk.CTkFrame(page, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=2)
        main_content.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls
        left_panel = ctk.CTkFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Upload section
        upload_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        upload_section.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            upload_section,
            text="📁 UPLOAD IMAGES (max 50)",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_cyan']
        ).pack(anchor="w")
        
        self.crop_upload_btn = ctk.CTkButton(
            upload_section,
            text="⬆ Upload Images (1–50)",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.upload_crop_image
        )
        self.crop_upload_btn.pack(fill="x", pady=(15, 10))
        
        self.crop_image_label = ctk.CTkLabel(
            upload_section,
            text="No image selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.crop_image_label.pack(anchor="w")
        
        # Save directory
        self.crop_save_btn = ctk.CTkButton(
            upload_section,
            text="💾 Select Save Folder",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.select_crop_save_directory
        )
        self.crop_save_btn.pack(fill="x", pady=(15, 10))
        
        self.crop_save_label = ctk.CTkLabel(
            upload_section,
            text="No folder selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.crop_save_label.pack(anchor="w")
        
        # Separator
        ctk.CTkFrame(left_panel, height=1, fg_color=self.colors['border']).pack(fill="x", padx=20, pady=15)
        
        # Crop controls
        crop_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        crop_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            crop_section,
            text="📐 CROP MARGINS (pixels)",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_pink']
        ).pack(anchor="w")
        
        # Top crop
        top_frame = ctk.CTkFrame(crop_section, fg_color="transparent")
        top_frame.pack(fill="x", pady=(15, 10))
        
        ctk.CTkLabel(
            top_frame,
            text="Top:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_primary'],
            width=60
        ).pack(side="left")
        
        self.crop_top = ctk.CTkEntry(
            top_frame,
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            border_color=self.colors['border'],
            corner_radius=8,
            height=35,
            placeholder_text="0"
        )
        self.crop_top.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.crop_top.insert(0, "0")
        
        # Bottom crop
        bottom_frame = ctk.CTkFrame(crop_section, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            bottom_frame,
            text="Bottom:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_primary'],
            width=60
        ).pack(side="left")
        
        self.crop_bottom = ctk.CTkEntry(
            bottom_frame,
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            border_color=self.colors['border'],
            corner_radius=8,
            height=35,
            placeholder_text="0"
        )
        self.crop_bottom.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.crop_bottom.insert(0, "0")
        
        # Left crop
        left_frame = ctk.CTkFrame(crop_section, fg_color="transparent")
        left_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            left_frame,
            text="Left:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_primary'],
            width=60
        ).pack(side="left")
        
        self.crop_left = ctk.CTkEntry(
            left_frame,
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            border_color=self.colors['border'],
            corner_radius=8,
            height=35,
            placeholder_text="0"
        )
        self.crop_left.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.crop_left.insert(0, "0")
        
        # Right crop
        right_frame = ctk.CTkFrame(crop_section, fg_color="transparent")
        right_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            right_frame,
            text="Right:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_primary'],
            width=60
        ).pack(side="left")
        
        self.crop_right = ctk.CTkEntry(
            right_frame,
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            border_color=self.colors['border'],
            corner_radius=8,
            height=35,
            placeholder_text="0"
        )
        self.crop_right.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.crop_right.insert(0, "0")
        
        # Crop button
        self.crop_btn = ctk.CTkButton(
            left_panel,
            text="✂️ APPLY CROP",
            font=("Orbitron", 16, "bold"),
            fg_color=self.colors['neon_pink'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=15,
            height=55,
            command=self.apply_crop
        )
        self.crop_btn.pack(fill="x", padx=20, pady=20)
        
        def _on_crop_param_change(_event=None):
            if getattr(self, "crop_image_paths", None):
                self.display_crop_preview()
        
        for _w in (self.crop_top, self.crop_bottom, self.crop_left, self.crop_right):
            _w.bind("<KeyRelease>", _on_crop_param_change)
        
        # Right panel - Preview
        right_panel = ctk.CTkFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Preview header
        preview_header = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        preview_header.pack(fill="x", padx=20, pady=15)
        preview_header.pack_propagate(False)
        
        ctk.CTkLabel(
            preview_header,
            text="👁️ ORIGINAL vs CROPPED",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_pink']
        ).pack(side="left")
        
        self.crop_gallery_counter = ctk.CTkLabel(
            preview_header,
            text="0 / 0",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_cyan']
        )
        self.crop_gallery_counter.pack(side="right")
        
        # Preview canvas
        self.crop_preview_canvas = tk.Canvas(
            right_panel,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.crop_preview_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 5))
        
        crop_nav_frame = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        crop_nav_frame.pack(fill="x", padx=20, pady=(5, 15))
        crop_nav_frame.pack_propagate(False)
        
        self.crop_prev_btn = ctk.CTkButton(
            crop_nav_frame, text="◀  Previous",
            font=("Rajdhani", 13, "bold"), width=120, height=36,
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12, command=self._crop_preview_prev,
            state="disabled"
        )
        self.crop_prev_btn.pack(side="left")
        
        self.crop_nav_filename = ctk.CTkLabel(
            crop_nav_frame, text="",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.crop_nav_filename.pack(side="left", expand=True)
        
        self.crop_next_btn = ctk.CTkButton(
            crop_nav_frame, text="Next  ▶",
            font=("Rajdhani", 13, "bold"), width=120, height=36,
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12, command=self._crop_preview_next,
            state="disabled"
        )
        self.crop_next_btn.pack(side="right")
        
        # Placeholder
        self.crop_preview_canvas.create_text(
            400, 300,
            text="📷 Upload an image to start cropping",
            font=("Rajdhani", 16),
            fill=self.colors['text_secondary'],
            justify="center"
        )
        
        return page
        
    def create_resizing_page(self):
        """Create the Resizing page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(page, fg_color="transparent", height=60)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📐 IMAGE RESIZING",
            font=("Orbitron", 24, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Resize with aspect ratio control",
            font=("Rajdhani", 14),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(20, 0))
        
        # Main content
        main_content = ctk.CTkFrame(page, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=2)
        main_content.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls
        left_panel = ctk.CTkScrollableFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Upload section
        upload_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        upload_section.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            upload_section,
            text="📁 UPLOAD IMAGES (max 50)",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_cyan']
        ).pack(anchor="w")
        
        self.resize_upload_btn = ctk.CTkButton(
            upload_section,
            text="⬆ Upload Images (1–50)",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.upload_resize_image
        )
        self.resize_upload_btn.pack(fill="x", pady=(15, 10))
        
        self.resize_image_label = ctk.CTkLabel(
            upload_section,
            text="No image selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.resize_image_label.pack(anchor="w")
        
        # Save directory
        self.resize_save_btn = ctk.CTkButton(
            upload_section,
            text="💾 Select Save Folder",
            font=("Rajdhani", 13, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12,
            height=45,
            command=self.select_resize_save_directory
        )
        self.resize_save_btn.pack(fill="x", pady=(15, 10))
        
        self.resize_save_label = ctk.CTkLabel(
            upload_section,
            text="No folder selected",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.resize_save_label.pack(anchor="w")
        
        # Separator
        ctk.CTkFrame(left_panel, height=1, fg_color=self.colors['border']).pack(fill="x", padx=20, pady=15)
        
        # Dimensions input
        dims_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        dims_section.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            dims_section,
            text="📐 CUSTOM DIMENSIONS",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_green']
        ).pack(anchor="w")
        
        # Width
        width_frame = ctk.CTkFrame(dims_section, fg_color="transparent")
        width_frame.pack(fill="x", pady=(15, 10))
        
        ctk.CTkLabel(
            width_frame,
            text="Width:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_primary'],
            width=70
        ).pack(side="left")
        
        self.resize_width = ctk.CTkEntry(
            width_frame,
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            border_color=self.colors['border'],
            corner_radius=8,
            height=35,
            placeholder_text="1920"
        )
        self.resize_width.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Height
        height_frame = ctk.CTkFrame(dims_section, fg_color="transparent")
        height_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            height_frame,
            text="Height:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_primary'],
            width=70
        ).pack(side="left")
        
        self.resize_height = ctk.CTkEntry(
            height_frame,
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            border_color=self.colors['border'],
            corner_radius=8,
            height=35,
            placeholder_text="1080"
        )
        self.resize_height.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        def _on_resize_dim_change(_event=None):
            if getattr(self, "resize_image_paths", None):
                self.display_resize_preview()
        
        self.resize_width.bind("<KeyRelease>", _on_resize_dim_change)
        self.resize_height.bind("<KeyRelease>", _on_resize_dim_change)
        
        # Maintain aspect ratio
        self.maintain_ratio = ctk.CTkCheckBox(
            dims_section,
            text="Maintain aspect ratio",
            font=("Rajdhani", 11),
            fg_color=self.colors['neon_green'],
            border_color=self.colors['border']
        )
        self.maintain_ratio.pack(anchor="w", pady=10)
        self.maintain_ratio.select()
        
        # Resize button
        self.resize_btn = ctk.CTkButton(
            left_panel,
            text="📐 RESIZE IMAGE",
            font=("Orbitron", 16, "bold"),
            fg_color=self.colors['neon_blue'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['text_primary'],
            corner_radius=15,
            height=55,
            command=self.apply_resize
        )
        self.resize_btn.pack(fill="x", padx=20, pady=20)
        
        # Right panel - Preview
        right_panel = ctk.CTkFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Preview header
        preview_header = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        preview_header.pack(fill="x", padx=20, pady=15)
        preview_header.pack_propagate(False)
        
        ctk.CTkLabel(
            preview_header,
            text="👁️ ORIGINAL vs RESIZED",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_pink']
        ).pack(side="left")
        
        self.resize_gallery_counter = ctk.CTkLabel(
            preview_header,
            text="0 / 0",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_cyan']
        )
        self.resize_gallery_counter.pack(side="right")
        
        # Preview canvas
        self.resize_preview_canvas = tk.Canvas(
            right_panel,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.resize_preview_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 5))
        
        resize_nav_frame = ctk.CTkFrame(right_panel, fg_color="transparent", height=50)
        resize_nav_frame.pack(fill="x", padx=20, pady=(5, 15))
        resize_nav_frame.pack_propagate(False)
        
        self.resize_prev_btn = ctk.CTkButton(
            resize_nav_frame, text="◀  Previous",
            font=("Rajdhani", 13, "bold"), width=120, height=36,
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12, command=self._resize_preview_prev,
            state="disabled"
        )
        self.resize_prev_btn.pack(side="left")
        
        self.resize_nav_filename = ctk.CTkLabel(
            resize_nav_frame, text="",
            font=("Rajdhani", 11),
            text_color=self.colors['text_secondary']
        )
        self.resize_nav_filename.pack(side="left", expand=True)
        
        self.resize_next_btn = ctk.CTkButton(
            resize_nav_frame, text="Next  ▶",
            font=("Rajdhani", 13, "bold"), width=120, height=36,
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_purple'],
            text_color=self.colors['text_primary'],
            corner_radius=12, command=self._resize_preview_next,
            state="disabled"
        )
        self.resize_next_btn.pack(side="right")
        
        # Placeholder
        self.resize_preview_canvas.create_text(
            400, 300,
            text="📷 Upload an image to start resizing",
            font=("Rajdhani", 16),
            fill=self.colors['text_secondary'],
            justify="center"
        )
        
        return page
        
    def create_live_page(self):
        """Create the Live Preview page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(page, fg_color="transparent", height=60)
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📹 LIVE PREVIEW",
            font=("Orbitron", 24, "bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="Real-time camera feed and folder monitoring",
            font=("Rajdhani", 14),
            text_color=self.colors['text_secondary']
        ).pack(side="left", padx=(20, 0))
        
        # Status indicator
        self.live_status = ctk.CTkFrame(
            header,
            fg_color=self.colors['bg_card'],
            corner_radius=15,
            width=150,
            height=40
        )
        self.live_status.pack(side="right")
        self.live_status.pack_propagate(False)
        
        self.status_dot = ctk.CTkLabel(
            self.live_status,
            text="●",
            font=("Segoe UI", 14),
            text_color=self.colors['neon_green']
        )
        self.status_dot.pack(side="left", padx=(15, 5))
        
        self.status_text = ctk.CTkLabel(
            self.live_status,
            text="LIVE",
            font=("Rajdhani", 12, "bold"),
            text_color=self.colors['neon_green']
        )
        self.status_text.pack(side="left")
        
        # Main content
        main_content = ctk.CTkFrame(page, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        main_content.grid_columnconfigure(0, weight=2)
        main_content.grid_columnconfigure(1, weight=1)
        main_content.grid_rowconfigure(0, weight=1)
        
        # Left - Main feed area
        feed_panel = ctk.CTkFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        feed_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Feed header
        feed_header = ctk.CTkFrame(feed_panel, fg_color="transparent", height=50)
        feed_header.pack(fill="x", padx=20, pady=15)
        feed_header.pack_propagate(False)
        
        ctk.CTkLabel(
            feed_header,
            text="📷 CAMERA FEED / FOLDER WATCH",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_cyan']
        ).pack(side="left")
        
        # Source selector
        self.live_source = ctk.CTkOptionMenu(
            feed_header,
            values=["Camera Feed", "Folder Watch"],
            font=("Rajdhani", 12),
            dropdown_font=("Rajdhani", 11),
            fg_color=self.colors['bg_hover'],
            button_color=self.colors['neon_cyan'],
            button_hover_color=self.colors['neon_blue'],
            dropdown_fg_color=self.colors['bg_card'],
            corner_radius=8,
            width=150
        )
        self.live_source.pack(side="right")
        
        # Video canvas placeholder
        self.live_canvas = tk.Canvas(
            feed_panel,
            bg=self.colors['bg_dark'],
            highlightthickness=0
        )
        self.live_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.live_placeholder_text = self.live_canvas.create_text(
            500, 350,
            text="📹 LIVE FEED INITIALIZING...\n\nSelect a source to begin",
            font=("Orbitron", 18),
            fill=self.colors['neon_cyan'],
            justify="center"
        )
        
        # Right panel - Controls
        controls_panel = ctk.CTkFrame(
            main_content,
            fg_color=self.colors['bg_card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        controls_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Controls header
        controls_header = ctk.CTkFrame(controls_panel, fg_color="transparent", height=50)
        controls_header.pack(fill="x", padx=20, pady=15)
        controls_header.pack_propagate(False)
        
        ctk.CTkLabel(
            controls_header,
            text="⚙️ CONTROLS",
            font=("Rajdhani", 14, "bold"),
            text_color=self.colors['neon_purple']
        ).pack(side="left")
        
        # Control buttons
        controls_content = ctk.CTkFrame(controls_panel, fg_color="transparent")
        controls_content.pack(fill="x", padx=20, pady=10)
        
        # Start/Stop button
        self.live_toggle_btn = ctk.CTkButton(
            controls_content,
            text="▶ START LIVE FEED",
            font=("Orbitron", 14, "bold"),
            fg_color=self.colors['neon_green'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['bg_dark'],
            corner_radius=12,
            height=50,
            command=self.toggle_live_feed
        )
        self.live_toggle_btn.pack(fill="x", pady=(0, 15))
        
        # Camera settings
        ctk.CTkLabel(
            controls_content,
            text="📷 CAMERA SETTINGS",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_pink']
        ).pack(anchor="w", pady=(15, 10))
        
        # Resolution selector
        ctk.CTkLabel(
            controls_content,
            text="Resolution:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w")
        
        self.cam_resolution = ctk.CTkOptionMenu(
            controls_content,
            values=["1920x1080", "1280x720", "640x480"],
            font=("Rajdhani", 11),
            fg_color=self.colors['bg_hover'],
            button_color=self.colors['neon_pink'],
            corner_radius=8
        )
        self.cam_resolution.pack(fill="x", pady=(5, 15))
        
        # FPS selector
        ctk.CTkLabel(
            controls_content,
            text="Frame Rate:",
            font=("Rajdhani", 12),
            text_color=self.colors['text_secondary']
        ).pack(anchor="w")
        
        self.cam_fps = ctk.CTkOptionMenu(
            controls_content,
            values=["30 FPS", "60 FPS", "120 FPS"],
            font=("Rajdhani", 11),
            fg_color=self.colors['bg_hover'],
            button_color=self.colors['neon_pink'],
            corner_radius=8
        )
        self.cam_fps.pack(fill="x", pady=(5, 15))
        
        # Separator
        ctk.CTkFrame(controls_content, height=1, fg_color=self.colors['border']).pack(fill="x", pady=15)
        
        # Folder watch settings
        ctk.CTkLabel(
            controls_content,
            text="📁 FOLDER WATCH",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_blue']
        ).pack(anchor="w", pady=(5, 10))
        
        self.watch_folder_btn = ctk.CTkButton(
            controls_content,
            text="📂 Select Watch Folder",
            font=("Rajdhani", 12),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_blue'],
            text_color=self.colors['text_primary'],
            corner_radius=8,
            height=40
        )
        self.watch_folder_btn.pack(fill="x", pady=5)
        
        # Stats section
        ctk.CTkFrame(controls_content, height=1, fg_color=self.colors['border']).pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            controls_content,
            text="📊 STATISTICS",
            font=("Rajdhani", 13, "bold"),
            text_color=self.colors['neon_green']
        ).pack(anchor="w", pady=(5, 10))
        
        stats_frame = ctk.CTkFrame(controls_content, fg_color=self.colors['bg_dark'], corner_radius=10)
        stats_frame.pack(fill="x", pady=5)
        
        self.stat_fps = ctk.CTkLabel(
            stats_frame,
            text="FPS: --",
            font=("Rajdhani", 12),
            text_color=self.colors['text_secondary']
        )
        self.stat_fps.pack(anchor="w", padx=15, pady=8)
        
        self.stat_frames = ctk.CTkLabel(
            stats_frame,
            text="Frames: --",
            font=("Rajdhani", 12),
            text_color=self.colors['text_secondary']
        )
        self.stat_frames.pack(anchor="w", padx=15, pady=8)
        
        self.stat_latency = ctk.CTkLabel(
            stats_frame,
            text="Latency: --ms",
            font=("Rajdhani", 12),
            text_color=self.colors['text_secondary']
        )
        self.stat_latency.pack(anchor="w", padx=15, pady=8)
        
        return page
        #it would alll start ferom here ,,,so i dont know what to write here but i know it would alll start ferom here
    # ==================== NAVIGATION ====================
    ## it started from all here in the show_page function from zain and eman
    def show_page(self, page_id):
        """Switch to the selected page"""
        if self.current_page == page_id:
            return
            
        # Update navigation button states
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=self.colors['bg_hover'])
                btn.icon_label.configure(text_color=btn.accent_color)
                btn.indicator.place(relx=0, rely=0.5, anchor="w")
                btn.text_label.configure(text_color=self.colors['text_primary'])
            else:
                btn.configure(fg_color="transparent")
                btn.icon_label.configure(text_color=self.colors['text_primary'])
                btn.indicator.place_forget()# left vertical bar would not be seen in this if its inactive
                btn.text_label.configure(text_color=self.colors['text_secondary'])
        
        # Hide current page and only make us vsble the selcted page only
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].pack_forget()
        
        # Snow its on on the official page of iursd we selcetd
        self.current_page = page_id
        page = self.pages[page_id]
        page.pack(fill="both", expand=True)
        
    # ==================== ENHANCE PAGE FUNCTIONS ====================
    
    def upload_enhance_images(self):
        files = filedialog.askopenfilenames(
            title=f"Select Images (max {MAX_PAGE_IMAGES})",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if files:
            if not self._check_image_count(len(files)):
                return
            self._load_enhance_images(list(files))

    def upload_enhance_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        if not folder:
            return
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
        files = []
        for root, _, fnames in os.walk(folder):
            for f in sorted(fnames):
                #this if changes the upper extension into lower xase extension ,JPG-> jpg
                if os.path.splitext(f)[1].lower() in exts:
                    files.append(os.path.join(root, f))
        if not files:
            messagebox.showwarning("No Images Found",
                f"No supported images found in:\n{folder}\n\nSupported: PNG, JPG, BMP, TIFF")
            return
        if not self._check_image_count(len(files)):
            return
        messagebox.showinfo("Folder Loaded", f"Found {len(files)} image(s) (max {MAX_PAGE_IMAGES} per page).")
        self._load_enhance_images(files)

    def _load_enhance_images(self, files):
        """Common handler after files are selected (from file or folder upload)."""
        if not self._check_image_count(len(files)):
            return
        # Invalidate prior enhancement + GT pairing (fresh dialog each load)
        self.batch_results = []# LIST THE IMAGES HERE
        self.gallery_index = 0# IT MNENA IT WIOLL START FROM TEH VERY FIRST IMAGE
        self._gallery_refs = []#Any cached image objects tied to the old gallery view are discarded so they do not mix with the new session.
        self._gallery_orig_img = None#This is the original image that was uploaded, it is used to display the original image in the gallery.
        self._gallery_enh_img = None#This is the enhanced image that was generated, it is used to display the enhanced image in the gallery.
        self._on_no_ground_truth_silent()
        self.uploaded_images = files
        self.current_image = Image.open(files[0])
        self.display_image_comparison()
        self.save_path_label.configure(text=f"{len(files)} image(s) selected")#this is the label that shows the number of images selected
        self._show_ground_truth_dialog()#this is the dialog that shows the ground truth image


    def select_save_directory(self):
        """Select save directory"""
        folder = filedialog.askdirectory(title="Select Save Directory")
        if folder:
            self.save_directory = folder
            display = folder if len(folder) < 40 else "..." + folder[-37:]
            self.save_path_label.configure(text=display)
            
    def update_model_description(self, model_name):
        """Update model description from the model_hooks registry"""
        info = model_hooks.ALL_MODELS.get(model_name)
        if info:
            self.model_desc.configure(text=f"{info['icon']}  {model_name}:\n{info['desc']}")
        else:
            self.model_desc.configure(text="")
        
    def toggle_hardware(self):
        """Toggle between CPU and GPU mode"""
        if self.hardware_switch.get():
            self.processing_mode = "GPU"
            self.cpu_label.configure(text_color=self.colors['text_secondary'])
            self.gpu_label.configure(text_color=self.colors['neon_cyan'])
            self.hardware_status.configure(text="GPU MODE ACTIVE", text_color=self.colors['neon_cyan'])
        else:
            self.processing_mode = "CPU"
            self.cpu_label.configure(text_color=self.colors['neon_green'])
            self.gpu_label.configure(text_color=self.colors['text_secondary'])
            self.hardware_status.configure(text="CPU MODE ACTIVE", text_color=self.colors['neon_green'])
            
    def clear_enhance_state(self):
        """Reset the Enhance page to its clean default state."""
        # Clear image lists
        self.uploaded_images = []
        self.ground_truth_images = []
        self.current_image = None
        self.enhanced_image = None

        # Clear gallery results
        self.batch_results = []
        self.gallery_index = 0
        self._gallery_refs = []

        # --- Reset the preview labels directly ---
        self.current_preview_image = None
        self._gallery_orig_img = None
        self._gallery_enh_img  = None
        self.preview_orig_label.config(image="", text="📷\n\nUpload images\nto see preview")
        self.preview_enh_label.config(image="", text="✨\n\nEnhanced result\nwill appear here")
        self.gallery_counter.configure(text="0 / 0")
        self.gallery_filename.configure(text="")

        # Reset progress widgets
        self.progress_frame.pack_forget()
        self.progress_bar.set(0)
        self.progress_label.configure(text="Processing... 0%")

        # Reset file / directory label
        self.save_path_label.configure(text="No directory selected")
        self.save_directory = ""

        # Reset model dropdown to default unsupervised list
        unsup_names = list(model_hooks.UNSUPERVISED_MODELS.keys())
        self.model_dropdown.configure(values=unsup_names)
        if unsup_names:
            self.model_dropdown.set(unsup_names[0])
            self.update_model_description(unsup_names[0])

        # Re-enable enhance button
        self.enhance_btn.configure(state="normal")
        self._refresh_gt_metrics_panel()

    def enhance_image(self):
        """Enhance the uploaded image"""
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return
            
        if not self.save_directory:
            messagebox.showwarning("Warning", "Please select a save directory!")
            return
            
        # Show progress
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        self.enhance_btn.configure(state="disabled")
        
        # Run enhancement in thread
        thread = threading.Thread(target=self._enhance_thread)
        thread.start()
        
    def _enhance_thread(self):
        """Enhancement processing thread — batch processes ALL uploaded images."""
        try:
            import time
            import torch
            
            # Smart CPU/GPU fallback logic
            if self.processing_mode == "GPU":
                if torch.cuda.is_available():
                    device = "cuda"
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Hardware Warning", 
                        "CUDA GPU not detected on this system.\nFalling back to CPU processing."
                    ))
                    device = "cpu"
            else:
                device = "cpu"
                
            total = len(self.uploaded_images)
            
            # Look up model function from the registry
            # Always read directly from the dropdown to get what user selected
            current_model = self.model_var.get()
            model_info = model_hooks.ALL_MODELS.get(current_model)
            if model_info is None:
                raise ValueError(f"Unknown model: {current_model!r}. Available: {list(model_hooks.ALL_MODELS.keys())}")
            fn = model_info["fn"]
            is_supervised = current_model in model_hooks.SUPERVISED_MODELS
            
            results = []  # (orig_path, enhanced_PIL)
            
            for idx, image_path in enumerate(self.uploaded_images):
                # Update progress
                pct = (idx + 1) / total
                label_text = f"Processing image {idx + 1}/{total}... {int(pct * 100)}%"
                self.after(0, lambda p=pct: self.progress_bar.set(p))
                self.after(0, lambda t=label_text: self.progress_label.configure(text=t))
                
                # Get GT path for this image (if supervised)
                gt_path = None
                if is_supervised and self.ground_truth_images:
                    if idx < len(self.ground_truth_images):
                        gt_path = self.ground_truth_images[idx]
                
                # Run model
                if is_supervised:
                    enhanced = fn(image_path, device=device, gt_path=gt_path)# GO TYO THE TEACHER BIO NADNMET ON THE LINE 45 TO 56
                else:
                    enhanced = fn(image_path, device=device)
                
                results.append((image_path, enhanced))#SAVE THE IMAGE HERE,,GALLERY WILL USE IT LATER
                
                # Save enhanced image
                base = os.path.splitext(os.path.basename(image_path))[0]#this is the base name of the image
                filename = f"{base}_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"#this is the filename of the enhanced image WITH THE TIME STAMP
                filepath = os.path.join(self.save_directory, filename)#this is the path of the enhanced image WITH TH FULL PATH
                enhanced.save(filepath)#this is the save path of the enhanced image
                
                time.sleep(0.05)  # small delay for UI responsiveness
            
            self.batch_results = results#SAVE THE IMAGES HERE,,GALLERY WILL USE IT LATER
            self.enhanced_image = results[0][1] if results else None#this is the enhanced image that was generated, it is used to display the enhanced image in the gallery.
            self.after(0, self.enhancement_complete)#this is the function that will be called when the enhancement is complete
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))#this is the error message that will be shown if the enhancement is not complete
            self.after(0, lambda: self.enhance_btn.configure(state="normal"))#
            self.after(0, lambda: self.progress_frame.pack_forget())#So basically, lambda: creates a tiny protective box around your code so it doesn't run instantly, and hands that box to self.after to open and run safely on the Main UI thread!
            
    # ═══════════════════════════════════════════════════════════════
    #  GROUND TRUTH DIALOG & CONDITIONAL MODEL SELECTION
    # ═══════════════════════════════════════════════════════════════
    
    #this swillll show the gt widget 
    def _show_ground_truth_dialog(self):
        """Show a futuristic CTkToplevel asking about ground truth."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ground Truth Check")
        dialog.geometry("480x280")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.colors['bg_dark'])
        dialog.grab_set()  # Modal,,it cant touch anything any screen unless click yes or np
        dialog.focus_force()#only wait on this widget
        
        # Center on parent
        dialog.transient(self)
        
        # Icon
        ctk.CTkLabel(
            dialog, text="🔍", font=("Segoe UI", 48)
        ).pack(pady=(24, 8))
        
        # Question
        ctk.CTkLabel(
            dialog,
            text="Do you have a ground truth (reference)\nimage for this file?",
            font=("Rajdhani", 16, "bold"),
            text_color=self.colors['text_primary'],
            justify="center"
        ).pack(pady=(0, 6))
        
        ctk.CTkLabel(
            dialog,
            text="This determines which models are available.",
            font=("Rajdhani", 12),
            text_color=self.colors['text_secondary']
        ).pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40)
        
        ctk.CTkButton(
            btn_frame, text="✗  No Ground Truth",
            font=("Rajdhani", 14, "bold"),
            fg_color=self.colors['bg_hover'],
            hover_color=self.colors['neon_cyan'],
            text_color=self.colors['text_primary'],
            corner_radius=14, height=44, width=180,
            command=lambda: self._on_no_ground_truth(dialog)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame, text="✓  Yes, Upload GT",
            font=("Rajdhani", 14, "bold"),
            fg_color=self.colors['neon_purple'],
            hover_color=self.colors['neon_pink'],
            text_color=self.colors['text_primary'],
            corner_radius=14, height=44, width=180,
            command=lambda: self._on_yes_ground_truth(dialog)
        ).pack(side="left")
    
    def _on_no_ground_truth(self, dialog):
        """User has no GT — show unsupervised models only."""
        dialog.destroy()
        self.ground_truth_images = []
        
        # Update dropdown to unsupervised models only
        names = list(model_hooks.UNSUPERVISED_MODELS.keys())
        self.model_dropdown.configure(values=names)
        self.model_var.set(names[0])
        self.model_dropdown.set(names[0])
        self.update_model_description(names[0])
        
        # Visual feedback
        self.model_desc.configure(
            text=f"Mode: Unsupervised (no GT)\n"
                 f"Available: {', '.join(names)}")
        self._refresh_gt_metrics_panel()
    
    def _on_yes_ground_truth(self, dialog):
        """User has GT — prompt batch upload, validate count, show supervised models."""
        dialog.destroy()
        
        gt_files = filedialog.askopenfilenames(
            title=f"Select {len(self.uploaded_images)} Ground Truth Image(s)",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if not gt_files:
            # Cancelled — fall back to unsupervised
            self._on_no_ground_truth_silent()
            return
        
        gt_files = list(gt_files)
        expected = len(self.uploaded_images)
        
        # Validate: GT count must match input count
        if len(gt_files) != expected:
            messagebox.showwarning(
                "Count Mismatch",
                f"You uploaded {expected} low-light image(s) but selected "
                f"{len(gt_files)} ground truth image(s).\n\n"
                f"Please select exactly {expected} GT image(s), one per input.\n"
                f"Falling back to unsupervised mode."
            )
            self._on_no_ground_truth_silent()
            return
        
        self.ground_truth_images = gt_files
        
        # Update dropdown to supervised models only
        names = list(model_hooks.SUPERVISED_MODELS.keys())
        self.model_dropdown.configure(values=names)
        self.model_var.set(names[0])
        self.model_dropdown.set(names[0])
        self.update_model_description(names[0])
        
        # Visual feedback
        self.model_desc.configure(
            text=f"Mode: Supervised ({len(gt_files)} GT loaded)\n"
                 f"Available: {', '.join(names)}")
        self._refresh_gt_metrics_panel()
    
    def _on_no_ground_truth_silent(self):
        """Fallback when user cancels GT upload."""
        self.ground_truth_images = []
        names = list(model_hooks.UNSUPERVISED_MODELS.keys())
        self.model_dropdown.configure(values=names)
        self.model_var.set(names[0])
        self.model_dropdown.set(names[0])
        self.update_model_description(names[0])
        self._refresh_gt_metrics_panel()
        
    def enhancement_complete(self):
        """Called when batch enhancement is complete."""
        self.progress_frame.pack_forget()
        self.enhance_btn.configure(state="normal")
        self.progress_bar.set(0)
        
        # Load gallery with first result
        if self.batch_results:
            self.gallery_index = 0
            self._gallery_show()
        
        n = len(self.batch_results)
        messagebox.showinfo(
            "Success",
            f"{n} image{'s' if n != 1 else ''} enhanced and saved!"
        )
    
    # ═══════════════════════════════════════════════════════════════
    #  GALLERY PREVIEW — split-screen with Next / Previous
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def _lanczos_resample():
        r = getattr(Image, "Resampling", None)
        if r is not None:
            return r.LANCZOS
        return Image.LANCZOS
    
    def _enhanced_to_pil_rgb(self, enhanced):
        """Normalize model output to RGB PIL for metrics."""
        if isinstance(enhanced, Image.Image):
            return enhanced.convert("RGB")
        if isinstance(enhanced, np.ndarray):
            a = enhanced
            if a.ndim == 3 and a.shape[2] >= 3:
                a = a[:, :, :3]
            if a.dtype in (np.float32, np.float64) and float(a.max()) <= 1.5:
                a = (np.clip(a, 0.0, 1.0) * 255.0).round().astype(np.uint8)
            else:
                a = np.clip(a, 0, 255).astype(np.uint8)
            return Image.fromarray(a, mode="RGB")
        try:
            import torch
            if isinstance(enhanced, torch.Tensor):
                t = enhanced.detach().float().cpu()
                if t.ndim == 4:
                    t = t[0]
                if t.ndim == 3 and t.shape[0] in (1, 3):
                    t = t.permute(1, 2, 0)
                arr = t.numpy()
                if arr.ndim == 2:
                    arr = np.stack([arr] * 3, axis=-1)
                if float(arr.max()) <= 1.5:
                    arr = (np.clip(arr, 0.0, 1.0) * 255.0).round()
                arr = np.clip(arr, 0, 255).astype(np.uint8)
                return Image.fromarray(arr, mode="RGB")
        except Exception:
            pass
        raise TypeError(f"Cannot convert enhanced output to PIL (got {type(enhanced)!r})")
    
    def _psnr_ssim_vs_gt(self, enhanced_pil, gt_path):
        """PSNR / SSIM between enhanced output and GT; GT is resized to output size."""
        gt = Image.open(gt_path).convert("RGB")
        pred = self._enhanced_to_pil_rgb(enhanced_pil)
        pred_arr = np.asarray(pred, dtype=np.float64)
        rs = self._lanczos_resample()
        gt_rs = gt.resize(pred.size, rs)
        gt_arr = np.asarray(gt_rs, dtype=np.float64)
        mse = np.mean((pred_arr - gt_arr) ** 2)
        if mse < 1e-12:
            psnr = 99.99
        else:
            psnr = 10.0 * np.log10((255.0 * 255.0) / mse)
        pred_u8 = np.clip(pred_arr, 0.0, 255.0).astype(np.uint8)
        gt_u8 = np.clip(gt_arr, 0.0, 255.0).astype(np.uint8)
        try:
            from skimage.metrics import structural_similarity as ssim_fn
            try:
                ssim_val = float(ssim_fn(pred_u8, gt_u8, channel_axis=2, data_range=255))
            except TypeError:
                ssim_val = float(ssim_fn(pred_u8, gt_u8, multichannel=True, data_range=255))
        except Exception:
            ssim_val = float("nan")
        return float(psnr), ssim_val
    
    def _refresh_gt_metrics_panel(self):
        """Update left-panel PSNR/SSIM when GT is loaded and (optional) results exist."""
        if not getattr(self, "metric_psnr_label", None):
            return
        if not self.ground_truth_images:
            self.metric_psnr_label.configure(text="PSNR: —")
            self.metric_ssim_label.configure(text="SSIM: —")
            self.metric_mean_label.configure(
                text="Select GT with upload to enable metrics."
            )
            return
        if not self.batch_results:
            self.metric_psnr_label.configure(text="PSNR: —")
            self.metric_ssim_label.configure(text="SSIM: —")
            self.metric_mean_label.configure(
                text="Enhance to compute vs your GT (GT resized to output)."
            )
            return
        idx = self.gallery_index
        n_gt = len(self.ground_truth_images)
        n_res = len(self.batch_results)
        pairable = min(n_gt, n_res)
        if pairable == 0:
            self.metric_psnr_label.configure(text="PSNR: —")
            self.metric_ssim_label.configure(text="SSIM: —")
            self.metric_mean_label.configure(text="")
            return
        if idx >= pairable:
            self.metric_psnr_label.configure(text="PSNR: —")
            self.metric_ssim_label.configure(text="SSIM: —")
            self.metric_mean_label.configure(
                text=f"No metric for image {idx + 1}: need ≥{idx + 1} GT and result rows (have {n_gt} GT, {n_res} outputs)."
            )
            self.update_idletasks()
            return
        warn = ""
        if n_gt != n_res:
            warn = f" Note: {n_gt} GT vs {n_res} outputs — using first {pairable} pairs only."
        try:
            _, enh = self.batch_results[idx]
            gt_path = self.ground_truth_images[idx]
            psnr, ssim = self._psnr_ssim_vs_gt(enh, gt_path)
            psnr_f = float(np.asarray(psnr).item())
            ssim_f = float(np.asarray(ssim).item()) if not isinstance(ssim, float) else ssim
            ssim_txt = ("%.4f" % ssim_f) if not math.isnan(ssim_f) else "—"
            self.metric_psnr_label.configure(text="PSNR: %.2f dB" % psnr_f)
            self.metric_ssim_label.configure(text="SSIM: " + ssim_txt)
            psnrs, ssims = [], []
            for i in range(pairable):
                _, e = self.batch_results[i]
                p, s = self._psnr_ssim_vs_gt(e, self.ground_truth_images[i])
                psnrs.append(float(np.asarray(p).item()))
                sf = float(np.asarray(s).item()) if not isinstance(s, float) else s
                if not math.isnan(sf):
                    ssims.append(sf)
            mean_psnr = float(np.mean(psnrs)) if psnrs else 0.0
            mean_ssim = float(np.mean(ssims)) if ssims else float("nan")
            mean_ssim_txt = ("%.4f" % mean_ssim) if not math.isnan(mean_ssim) else "—"
            self.metric_mean_label.configure(
                text=("Batch mean: PSNR %.2f dB · SSIM %s" % (mean_psnr, mean_ssim_txt)) + warn
            )
        except Exception as ex:
            self.metric_psnr_label.configure(text="PSNR: error")
            self.metric_ssim_label.configure(text="SSIM: error")
            self.metric_mean_label.configure(text=str(ex)[:120])
        self.update_idletasks()
    
    def _gallery_show(self):
        """Display current gallery pair — native tk.Label.image approach (GC-proof)."""
        if not self.batch_results:
            self._gallery_orig_img = None
            self._gallery_enh_img  = None
            self.preview_orig_label.config(image="", text="📷\n\nUpload images\nto see preview")
            self.preview_enh_label.config(image="",  text="✨\n\nEnhanced result\nwill appear here")
            self.gallery_counter.configure(text="0 / 0")
            self.gallery_filename.configure(text="")
            self._refresh_gt_metrics_panel()
            return

        self.update_idletasks()
        idx   = self.gallery_index
        total = len(self.batch_results)
        orig_path, enhanced_pil = self.batch_results[idx]

        # Compute display size based on container
        try:
            w = self.preview_orig_label.winfo_width()  - 16
            h = self.preview_orig_label.winfo_height() - 16
        except Exception:
            w, h = 380, 420
        if w < 80: w = 380
        if h < 80: h = 420
        display_size = (w, h)

        # Resize both images to fit
        orig_pil = Image.open(orig_path).convert("RGB")
        orig_pil.thumbnail(display_size, Image.LANCZOS)
        enh_copy = enhanced_pil.copy().convert("RGB")
        enh_copy.thumbnail(display_size, Image.LANCZOS)

        # Create PhotoImages and pin to the widgets (GC-proof idiom)
        self._gallery_orig_img = ImageTk.PhotoImage(orig_pil)
        self._gallery_enh_img  = ImageTk.PhotoImage(enh_copy)
        self.preview_orig_label.image = self._gallery_orig_img  # pin to widget
        self.preview_enh_label.image  = self._gallery_enh_img   # pin to widget

        self.preview_orig_label.config(image=self._gallery_orig_img, text="")
        self.preview_enh_label.config(image=self._gallery_enh_img,   text="")

        self.gallery_counter.configure(text=f"{idx + 1} / {total}")
        self.gallery_filename.configure(text=os.path.basename(orig_path))
        self._refresh_gt_metrics_panel()

    def _gallery_next(self):
        """Navigate to next image in the batch."""
        if self.batch_results and self.gallery_index < len(self.batch_results) - 1:
            self.gallery_index += 1
            self._gallery_show()
    
    def _gallery_prev(self):
        """Navigate to previous image in the batch."""
        if self.batch_results and self.gallery_index > 0:
            self.gallery_index -= 1
            self._gallery_show()
    
    def display_image_comparison(self):
        """Show uploaed image preview in original slot — GC-proof tk.Label.image idiom."""
        if not self.current_image:
            return

        self.update_idletasks()
        try:
            w = self.preview_orig_label.winfo_width()  - 16
            h = self.preview_orig_label.winfo_height() - 16
        except Exception:
            w, h = 380, 420
        if w < 80: w = 380
        if h < 80: h = 420

        preview = self.current_image.copy().convert("RGB")
        preview.thumbnail((w, h), Image.LANCZOS)
        self.current_preview_image = ImageTk.PhotoImage(preview)
        self.preview_orig_label.image = self.current_preview_image  # pin to widget

        self.preview_orig_label.config(image=self.current_preview_image, text="")
        self.preview_enh_label.config(image="", text="✨\n\nEnhanced result\nwill appear here")
        self.gallery_counter.configure(text=f"1 / {len(self.uploaded_images)}")
        self.gallery_filename.configure(
            text=os.path.basename(self.uploaded_images[0]) if self.uploaded_images else ""
        )

    # ==================== AUGMENTATION PAGE FUNCTIONS ====================
    
    def upload_augment_images(self):
        """Upload images for augmentation"""
        files = filedialog.askopenfilenames(
            title=f"Select Images (max {MAX_PAGE_IMAGES})",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if files:
            if not self._check_image_count(len(files)):
                return
            self.aug_images = list(files)
            self.aug_count_label.configure(text=f"{len(files)} images selected")
            
    def select_aug_save_directory(self):
        """Select augmentation save directory"""
        folder = filedialog.askdirectory(title="Select Save Folder")
        if folder:
            self.aug_save_dir = folder
            display = folder if len(folder) < 40 else "..." + folder[-37:]
            self.aug_save_label.configure(text=display)
            
    def generate_augmented_data(self):
        """Generate 90, 180, and 270 degree rotated images."""
        if not hasattr(self, 'aug_images') or not self.aug_images:
            messagebox.showwarning("Warning", "Please upload images first!")
            return
            
        if not hasattr(self, 'aug_save_dir') or not self.aug_save_dir:
            messagebox.showwarning("Warning", "Please select a save folder!")
            return
            
        self.aug_generate_btn.configure(state="disabled", text="⏳ Generating...")
        
        # Run in thread so UI stays responsive
        def _aug_worker():
            total_saved = 0
            try:
                for img_path in self.aug_images:
                    img = Image.open(img_path).convert("RGB")
                    base = os.path.splitext(os.path.basename(img_path))[0]
                    
                    # Generate 90, 180, 270 rotations
                    angles = [90, 180, 270]
                    for angle in angles:
                        # expand=True to ensure corners aren't cut if the image is not perfectly square
                        augmented = img.rotate(angle, expand=True) 
                        
                        filename = f"{base}_rot{angle}.png"
                        filepath = os.path.join(self.aug_save_dir, filename)
                        augmented.save(filepath)
                        total_saved += 1
                
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Generated {total_saved} rotated images (90°, 180°, 270°)!\nSaved to: {self.aug_save_dir}"
                ))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.after(0, lambda: self.aug_generate_btn.configure(
                    state="normal", text="🔄 GENERATE AUGMENTED DATA"
                ))
        
        threading.Thread(target=_aug_worker, daemon=True).start()
        
    # ==================== CROPPING PAGE FUNCTIONS ====================
    
    def upload_crop_image(self):
        """Upload one or more images for cropping (same crop values applied to each, max 50)."""
        files = filedialog.askopenfilenames(
            title=f"Select Images (max {MAX_PAGE_IMAGES})",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if not files:
            return
        if not self._check_image_count(len(files)):
            return
        self.crop_image_paths = list(files)
        self.crop_preview_index = 0
        self.crop_image = Image.open(files[0]).convert("RGB")
        if hasattr(self, "cropped_result"):
            del self.cropped_result
        if len(files) == 1:
            self.crop_image_label.configure(text=os.path.basename(files[0]))
        else:
            self.crop_image_label.configure(
                text=f"{len(files)} images — preview: {os.path.basename(files[0])}"
            )
        self.display_crop_preview()
            
    def select_crop_save_directory(self):
        """Select crop save directory"""
        folder = filedialog.askdirectory(title="Select Save Folder")
        if folder:
            self.crop_save_dir = folder
            display = folder if len(folder) < 40 else "..." + folder[-37:]
            self.crop_save_label.configure(text=display)
            
    def apply_crop(self):
        """Apply crop to all selected images (same top/bottom/left/right for each)."""
        paths = getattr(self, "crop_image_paths", None)
        if not paths:
            messagebox.showwarning("Warning", "Please upload image(s) first!")
            return
            
        try:
            top = int(self.crop_top.get())
            bottom = int(self.crop_bottom.get())
            left = int(self.crop_left.get())
            right = int(self.crop_right.get())
            
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved = 0
            last_cropped = None
            for i, pth in enumerate(paths):
                img = Image.open(pth).convert("RGB")
                w, h = img.size
                cropped = img.crop((left, top, w - right, h - bottom))
                last_cropped = cropped
                if hasattr(self, "crop_save_dir") and self.crop_save_dir:
                    base = os.path.splitext(os.path.basename(pth))[0]
                    filename = f"{base}_cropped_{ts}_{i:03d}.png"
                    filepath = os.path.join(self.crop_save_dir, filename)
                    cropped.save(filepath)
                    saved += 1
            if saved:
                messagebox.showinfo(
                    "Success",
                    f"Saved {saved} cropped image(s)." if saved > 1 else "Cropped image saved!",
                )
            self.cropped_result = last_cropped
            self.display_crop_preview()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _crop_preview_prev(self):
        paths = getattr(self, "crop_image_paths", None)
        if not paths or self.crop_preview_index <= 0:
            return
        self.crop_preview_index -= 1
        self.display_crop_preview()
        
    def _crop_preview_next(self):
        paths = getattr(self, "crop_image_paths", None)
        if not paths or self.crop_preview_index >= len(paths) - 1:
            return
        self.crop_preview_index += 1
        self.display_crop_preview()
        
    def display_crop_preview(self):
        """Display crop preview for the current image (live crop from entries)."""
        self.crop_preview_canvas.delete("all")
        
        paths = getattr(self, "crop_image_paths", None)
        if not paths and not hasattr(self, "crop_image"):
            self.crop_gallery_counter.configure(text="0 / 0")
            self.crop_nav_filename.configure(text="")
            self.crop_prev_btn.configure(state="disabled")
            self.crop_next_btn.configure(state="disabled")
            self.crop_preview_canvas.create_text(
                400, 300,
                text="📷 Upload an image to start cropping",
                font=("Rajdhani", 16),
                fill=self.colors['text_secondary'],
                justify="center"
            )
            return
        
        if paths:
            self.crop_preview_index = max(
                0, min(self.crop_preview_index, len(paths) - 1)
            )
            self.crop_image = Image.open(paths[self.crop_preview_index]).convert("RGB")
            n = len(paths)
            self.crop_gallery_counter.configure(
                text=f"{self.crop_preview_index + 1} / {n}"
            )
            self.crop_nav_filename.configure(
                text=os.path.basename(paths[self.crop_preview_index])
            )
            self.crop_prev_btn.configure(
                state="normal" if self.crop_preview_index > 0 else "disabled"
            )
            self.crop_next_btn.configure(
                state="normal" if self.crop_preview_index < n - 1 else "disabled"
            )
        else:
            self.crop_gallery_counter.configure(text="1 / 1")
            self.crop_nav_filename.configure(text="")
            self.crop_prev_btn.configure(state="disabled")
            self.crop_next_btn.configure(state="disabled")
            
        canvas_width = self.crop_preview_canvas.winfo_width() or 800
        canvas_height = self.crop_preview_canvas.winfo_height() or 600
        
        img_width = (canvas_width - 60) // 2
        img_height = canvas_height - 100
        
        # Original
        orig = self.crop_image.copy()
        orig.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
        self.crop_orig_photo = ImageTk.PhotoImage(orig)
        self.crop_preview_canvas.create_image(
            20, 50, anchor="nw", image=self.crop_orig_photo
        )
        self.crop_preview_canvas.create_text(
            20 + img_width // 2, 30,
            text="ORIGINAL",
            font=("Orbitron", 12, "bold"),
            fill=self.colors['text_secondary']
        )
        
        cropped_preview = None
        try:
            top = int(self.crop_top.get())
            bottom = int(self.crop_bottom.get())
            left = int(self.crop_left.get())
            right = int(self.crop_right.get())
            w, h = self.crop_image.size
            if left + right < w and top + bottom < h and left >= 0 and top >= 0:
                cropped_preview = self.crop_image.crop(
                    (left, top, w - right, h - bottom)
                )
        except (ValueError, TypeError):
            pass
        
        if cropped_preview is not None:
            cp = cropped_preview.copy()
            cp.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
            self.cropped_photo = ImageTk.PhotoImage(cp)
            self.crop_preview_canvas.create_image(
                40 + img_width, 50, anchor="nw", image=self.cropped_photo
            )
            self.crop_preview_canvas.create_text(
                40 + img_width + img_width // 2, 30,
                text="CROPPED",
                font=("Orbitron", 12, "bold"),
                fill=self.colors['neon_pink']
            )
        else:
            self.crop_preview_canvas.create_text(
                40 + img_width + img_width // 2,
                50 + img_height // 2,
                text="(invalid crop values)",
                font=("Rajdhani", 12),
                fill=self.colors['text_secondary'],
                justify="center"
            )
            
    # ==================== RESIZING PAGE FUNCTIONS ====================
    
    def upload_resize_image(self):
        """Upload one or more images for resizing (same target size for all, max 50)."""
        files = filedialog.askopenfilenames(
            title=f"Select Images (max {MAX_PAGE_IMAGES})",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
        )
        if not files:
            return
        if not self._check_image_count(len(files)):
            return
        self.resize_image_paths = list(files)
        self.resize_preview_index = 0
        self.resize_image = Image.open(files[0]).convert("RGB")
        if hasattr(self, "resized_result"):
            del self.resized_result
        if len(files) == 1:
            self.resize_image_label.configure(text=os.path.basename(files[0]))
        else:
            self.resize_image_label.configure(
                text=f"{len(files)} images — preview: {os.path.basename(files[0])}"
            )
        w, h = self.resize_image.size
        self.resize_width.delete(0, "end")
        self.resize_width.insert(0, str(w))
        self.resize_height.delete(0, "end")
        self.resize_height.insert(0, str(h))
        self.display_resize_preview()
            
    def select_resize_save_directory(self):
        """Select resize save directory"""
        folder = filedialog.askdirectory(title="Select Save Folder")
        if folder:
            self.resize_save_dir = folder
            display = folder if len(folder) < 40 else "..." + folder[-37:]
            self.resize_save_label.configure(text=display)
            
    def apply_resize(self):
        """Apply resize to all selected images (same width and height for each)."""
        paths = getattr(self, "resize_image_paths", None)
        if not paths:
            messagebox.showwarning("Warning", "Please upload image(s) first!")
            return
        
        if not hasattr(self, 'resize_save_dir') or not self.resize_save_dir:
            messagebox.showwarning("Warning", "Please select a save folder first!")
            return
            
        try:
            width = int(self.resize_width.get())
            height = int(self.resize_height.get())
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved = 0
            last_resized = None
            for i, pth in enumerate(paths):
                img = Image.open(pth).convert("RGB")
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                last_resized = resized
                base = os.path.splitext(os.path.basename(pth))[0]
                filename = f"{base}_resized_{ts}_{i:03d}.png"
                filepath = os.path.join(self.resize_save_dir, filename)
                resized.save(filepath)
                saved += 1
            messagebox.showinfo(
                "Success",
                f"Saved {saved} resized image(s)." if saved > 1 else "Resized image saved!",
            )
            self.resized_result = last_resized
            self.display_resize_preview()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _resize_preview_prev(self):
        paths = getattr(self, "resize_image_paths", None)
        if not paths or self.resize_preview_index <= 0:
            return
        self.resize_preview_index -= 1
        self.display_resize_preview()
        
    def _resize_preview_next(self):
        paths = getattr(self, "resize_image_paths", None)
        if not paths or self.resize_preview_index >= len(paths) - 1:
            return
        self.resize_preview_index += 1
        self.display_resize_preview()
        
    def display_resize_preview(self):
        """Display resize preview for the current image (live size from width/height entries)."""
        self.resize_preview_canvas.delete("all")
        
        paths = getattr(self, "resize_image_paths", None)
        if not paths and not hasattr(self, "resize_image"):
            self.resize_gallery_counter.configure(text="0 / 0")
            self.resize_nav_filename.configure(text="")
            self.resize_prev_btn.configure(state="disabled")
            self.resize_next_btn.configure(state="disabled")
            self.resize_preview_canvas.create_text(
                400, 300,
                text="📷 Upload an image to start resizing",
                font=("Rajdhani", 16),
                fill=self.colors['text_secondary'],
                justify="center"
            )
            return
        
        if paths:
            self.resize_preview_index = max(
                0, min(self.resize_preview_index, len(paths) - 1)
            )
            self.resize_image = Image.open(paths[self.resize_preview_index]).convert("RGB")
            n = len(paths)
            self.resize_gallery_counter.configure(
                text=f"{self.resize_preview_index + 1} / {n}"
            )
            self.resize_nav_filename.configure(
                text=os.path.basename(paths[self.resize_preview_index])
            )
            self.resize_prev_btn.configure(
                state="normal" if self.resize_preview_index > 0 else "disabled"
            )
            self.resize_next_btn.configure(
                state="normal" if self.resize_preview_index < n - 1 else "disabled"
            )
        else:
            self.resize_gallery_counter.configure(text="1 / 1")
            self.resize_nav_filename.configure(text="")
            self.resize_prev_btn.configure(state="disabled")
            self.resize_next_btn.configure(state="disabled")
            
        canvas_width = self.resize_preview_canvas.winfo_width() or 800
        canvas_height = self.resize_preview_canvas.winfo_height() or 600
        
        img_width = (canvas_width - 60) // 2
        img_height = canvas_height - 100
        
        # Original
        orig = self.resize_image.copy()
        orig.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
        self.resize_orig_photo = ImageTk.PhotoImage(orig)
        self.resize_preview_canvas.create_image(
            20, 50, anchor="nw", image=self.resize_orig_photo
        )
        self.resize_preview_canvas.create_text(
            20 + img_width // 2, 30,
            text="ORIGINAL",
            font=("Orbitron", 12, "bold"),
            fill=self.colors['text_secondary']
        )
        
        resized_preview = None
        try:
            width = int(self.resize_width.get())
            height = int(self.resize_height.get())
            if width > 0 and height > 0:
                resized_preview = self.resize_image.resize(
                    (width, height), Image.Resampling.LANCZOS
                )
        except (ValueError, TypeError):
            pass
        
        if resized_preview is not None:
            rs = resized_preview.copy()
            rs.thumbnail((img_width, img_height), Image.Resampling.LANCZOS)
            self.resized_photo = ImageTk.PhotoImage(rs)
            self.resize_preview_canvas.create_image(
                40 + img_width, 50, anchor="nw", image=self.resized_photo
            )
            self.resize_preview_canvas.create_text(
                40 + img_width + img_width // 2, 30,
                text="RESIZED",
                font=("Orbitron", 12, "bold"),
                fill=self.colors['neon_blue']
            )
        else:
            self.resize_preview_canvas.create_text(
                40 + img_width + img_width // 2,
                50 + img_height // 2,
                text="(invalid width / height)",
                font=("Rajdhani", 12),
                fill=self.colors['text_secondary'],
                justify="center"
            )
            
    # ==================== LIVE PAGE FUNCTIONS ====================
    
    def toggle_live_feed(self):
        """Toggle live feed on/off"""
        if self.live_toggle_btn.cget("text") == "▶ START LIVE FEED":
            self.live_toggle_btn.configure(
                text="⏹ STOP LIVE FEED",
                fg_color=self.colors['neon_pink'],
                hover_color="#d4004f"
            )
            self.status_dot.configure(text_color=self.colors['neon_pink'])
            self.status_text.configure(text="RECORDING", text_color=self.colors['neon_pink'])
        else:
            self.live_toggle_btn.configure(
                text="▶ START LIVE FEED",
                fg_color=self.colors['neon_green'],
                hover_color=self.colors['neon_cyan']
            )
            self.status_dot.configure(text_color=self.colors['neon_green'])
            self.status_text.configure(text="LIVE", text_color=self.colors['neon_green'])

# Run the application
if __name__ == "__main__":
    app = NeonEnhancerPro()
    app.mainloop()
