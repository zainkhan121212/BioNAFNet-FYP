#!/usr/bin/env python3
"""
ImageEnhancer Pro - Advanced Image Processing Suite
A professional, interactive image enhancement application built with Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import os
import threading
import random
import math
from datetime import datetime

class ImageEnhancerPro(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("ImageEnhancer Pro - Advanced Image Processing Suite")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Theme variables
        self.dark_mode = tk.BooleanVar(value=False)
        self.gpu_enabled = tk.BooleanVar(value=False)
        self.animation_active = False
        
        # Colors for themes
        self.colors = {
            'light': {
                'bg': '#f0f4f8',
                'sidebar': '#ffffff',
                'accent': '#6366f1',
                'accent_hover': '#4f46e5',
                'text': '#1e293b',
                'text_secondary': '#64748b',
                'border': '#e2e8f0',
                'card': '#ffffff',
                'success': '#10b981',
                'warning': '#f59e0b',
                'gpu_glow': '#06b6d4',
                'gpu_bg': '#0891b2'
            },
            'dark': {
                'bg': '#0f172a',
                'sidebar': '#1e293b',
                'accent': '#818cf8',
                'accent_hover': '#6366f1',
                'text': '#f1f5f9',
                'text_secondary': '#94a3b8',
                'border': '#334155',
                'card': '#1e293b',
                'success': '#34d399',
                'warning': '#fbbf24',
                'gpu_glow': '#22d3ee',
                'gpu_bg': '#0e7490'
            }
        }
        
        # Image storage
        self.uploaded_images = []
        self.current_image_index = 0
        self.enhanced_images = {}
        self.save_path = ""
        
        # Model selection
        self.selected_model = tk.StringVar(value="A")
        
        # Animation particles for GPU mode
        self.particles = []
        self.glow_intensity = 0
        self.glow_direction = 1
        
        self.setup_styles()
        self.create_ui()
        self.apply_theme()
        
    def setup_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background=self.colors['light']['bg'])
        
    def create_ui(self):
        """Create the main UI structure"""
        # Main container
        self.main_container = tk.Frame(self, bg=self.colors['light']['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Background canvas for animations
        # Background canvas for animations
        self.bg_canvas = tk.Canvas(self.main_container, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # We must make sure the canvas is actually rendered before lowering it
        # Tkinter will throw `wrong # args: should be ".!frame.!canvas lower tagOrId ?belowThis?"`
        # if you try to lower an empty canvas that hasn't been fully mapped to the window yet
        # in some versions/configurations. We'll defer the lowering slightly.
        # self.after(100, lambda: self.bg_canvas.lower())
        
        # Header with title and controls
        self.create_header()
        
        # Main content area
        self.content_frame = tk.Frame(self.main_container, bg=self.colors['light']['bg'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.content_frame.lift()
        
        # Left sidebar
        self.create_left_sidebar()
        
        # Center panel
        self.create_center_panel()
        
        # Right panel for models
        self.create_right_panel()
        
        # Bottom toolbar
        self.create_bottom_toolbar()
        
        # Start animations
        self.start_animations()
        
    def create_header(self):
        """Create animated header"""
        self.header = tk.Frame(self.main_container, height=70, bg=self.colors['light']['sidebar'])
        self.header.pack(fill=tk.X, padx=0, pady=0)
        self.header.pack_propagate(False)
        self.header.lift()
        
        # Logo and title with glow effect
        self.logo_frame = tk.Frame(self.header, bg=self.colors['light']['sidebar'])
        self.logo_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.logo_label = tk.Label(
            self.logo_frame,
            text="⚡",
            font=('Segoe UI', 28, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['accent']
        )
        self.logo_label.pack(side=tk.LEFT)
        
        self.title_label = tk.Label(
            self.logo_frame,
            text="ImageEnhancer Pro",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Version badge
        self.version_label = tk.Label(
            self.logo_frame,
            text="v2.0",
            font=('Segoe UI', 10),
            bg=self.colors['light']['accent'],
            fg='white',
            padx=8,
            pady=2
        )
        self.version_label.pack(side=tk.LEFT, pady=8)
        
        # Header controls
        self.controls_frame = tk.Frame(self.header, bg=self.colors['light']['sidebar'])
        self.controls_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # GPU Toggle with animated indicator
        self.gpu_frame = tk.Frame(self.controls_frame, bg=self.colors['light']['sidebar'])
        self.gpu_frame.pack(side=tk.LEFT, padx=10)
        
        self.gpu_indicator = tk.Canvas(
            self.gpu_frame,
            width=12,
            height=12,
            bg=self.colors['light']['sidebar'],
            highlightthickness=0
        )
        self.gpu_indicator.pack(side=tk.LEFT, padx=5)
        self.gpu_indicator.create_oval(2, 2, 10, 10, fill='#94a3b8', tags='indicator')
        
        self.gpu_btn = tk.Button(
            self.gpu_frame,
            text="GPU Processing",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text'],
            activebackground=self.colors['light']['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.toggle_gpu
        )
        self.gpu_btn.pack(side=tk.LEFT)
        
        # Theme toggle
        self.theme_btn = tk.Button(
            self.controls_frame,
            text="🌙 Dark Mode",
            font=('Segoe UI', 11),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text'],
            activebackground=self.colors['light']['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=10)
        
    def create_left_sidebar(self):
        """Create left sidebar with upload and save functionality"""
        self.left_sidebar = tk.Frame(
            self.content_frame,
            width=280,
            bg=self.colors['light']['sidebar'],
            highlightbackground=self.colors['light']['border'],
            highlightthickness=1
        )
        self.left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_sidebar.pack_propagate(False)
        
        # Upload Section
        self.upload_section = tk.Frame(self.left_sidebar, bg=self.colors['light']['sidebar'])
        self.upload_section.pack(fill=tk.X, padx=15, pady=15)
        
        self.upload_title = tk.Label(
            self.upload_section,
            text="📁 Upload Images",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.upload_title.pack(anchor=tk.W)
        
        self.upload_subtitle = tk.Label(
            self.upload_section,
            text="Drag & drop or browse files",
            font=('Segoe UI', 10),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary']
        )
        self.upload_subtitle.pack(anchor=tk.W, pady=(5, 10))
        
        # Upload button with hover effect
        self.upload_btn = tk.Button(
            self.upload_section,
            text="+ Upload Images",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['accent'],
            fg='white',
            activebackground=self.colors['light']['accent_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.upload_images
        )
        self.upload_btn.pack(fill=tk.X, pady=5)
        
        # Image counter
        self.image_counter = tk.Label(
            self.upload_section,
            text="0 images uploaded",
            font=('Segoe UI', 10),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary']
        )
        self.image_counter.pack(anchor=tk.W, pady=5)
        
        # Separator
        self.create_separator(self.left_sidebar)
        
        # Save Section
        self.save_section = tk.Frame(self.left_sidebar, bg=self.colors['light']['sidebar'])
        self.save_section.pack(fill=tk.X, padx=15, pady=15)
        
        self.save_title = tk.Label(
            self.save_section,
            text="💾 Save Results",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.save_title.pack(anchor=tk.W)
        
        # Folder path display
        self.path_frame = tk.Frame(self.save_section, bg=self.colors['light']['sidebar'])
        self.path_frame.pack(fill=tk.X, pady=10)
        
        self.path_label = tk.Label(
            self.path_frame,
            text="Save Location:",
            font=('Segoe UI', 10),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary']
        )
        self.path_label.pack(anchor=tk.W)
        
        self.path_display = tk.Label(
            self.path_frame,
            text="Not selected",
            font=('Segoe UI', 9),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text_secondary'],
            wraplength=230,
            padx=10,
            pady=5
        )
        self.path_display.pack(fill=tk.X, pady=5)
        
        # Browse button
        self.browse_btn = tk.Button(
            self.save_section,
            text="📂 Choose Folder",
            font=('Segoe UI', 11),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text'],
            activebackground=self.colors['light']['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.choose_save_location
        )
        self.browse_btn.pack(fill=tk.X, pady=5)
        
        # New folder button
        self.new_folder_btn = tk.Button(
            self.save_section,
            text="📁 Create New Folder",
            font=('Segoe UI', 11),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text'],
            activebackground=self.colors['light']['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.create_new_folder
        )
        self.new_folder_btn.pack(fill=tk.X, pady=5)
        
        # Save button
        self.save_btn = tk.Button(
            self.save_section,
            text="💾 Save Selected",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['success'],
            fg='white',
            activebackground='#059669',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.save_images
        )
        self.save_btn.pack(fill=tk.X, pady=10)
        
        # Separator
        self.create_separator(self.left_sidebar)
        
        # Image list
        self.list_section = tk.Frame(self.left_sidebar, bg=self.colors['light']['sidebar'])
        self.list_section.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.list_title = tk.Label(
            self.list_section,
            text="📋 Uploaded Images",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.list_title.pack(anchor=tk.W)
        
        # Scrollable image list
        self.list_scroll = tk.Scrollbar(self.list_section)
        self.list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.list_canvas = tk.Canvas(
            self.list_section,
            bg=self.colors['light']['sidebar'],
            highlightthickness=0,
            yscrollcommand=self.list_scroll.set
        )
        self.list_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        self.list_scroll.config(command=self.list_canvas.yview)
        
        self.image_list_frame = tk.Frame(self.list_canvas, bg=self.colors['light']['sidebar'])
        self.list_canvas.create_window((0, 0), window=self.image_list_frame, anchor=tk.NW, width=240)
        
        self.image_list_frame.bind("<Configure>", lambda e: self.list_canvas.configure(
            scrollregion=self.list_canvas.bbox("all")))
        
    def create_center_panel(self):
        """Create center panel for image viewing and comparison"""
        self.center_panel = tk.Frame(
            self.content_frame,
            bg=self.colors['light']['bg']
        )
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image viewer frame
        self.viewer_frame = tk.Frame(
            self.center_panel,
            bg=self.colors['light']['card'],
            highlightbackground=self.colors['light']['border'],
            highlightthickness=2
        )
        self.viewer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Viewer header
        self.viewer_header = tk.Frame(
            self.viewer_frame,
            bg=self.colors['light']['card'],
            height=40
        )
        self.viewer_header.pack(fill=tk.X, padx=10, pady=5)
        self.viewer_header.pack_propagate(False)
        
        self.viewer_title = tk.Label(
            self.viewer_header,
            text="🖼️ Image Preview & Comparison",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['card'],
            fg=self.colors['light']['text']
        )
        self.viewer_title.pack(side=tk.LEFT, pady=5)
        
        # Comparison toggle
        self.compare_var = tk.BooleanVar(value=False)
        self.compare_check = tk.Checkbutton(
            self.viewer_header,
            text="Side-by-side Compare",
            variable=self.compare_var,
            font=('Segoe UI', 10),
            bg=self.colors['light']['card'],
            fg=self.colors['light']['text'],
            selectcolor=self.colors['light']['accent'],
            activebackground=self.colors['light']['card'],
            command=self.toggle_comparison
        )
        self.compare_check.pack(side=tk.RIGHT, pady=5)
        
        # Image canvas
        self.image_canvas = tk.Canvas(
            self.viewer_frame,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.image_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Placeholder text
        self.placeholder_text = self.image_canvas.create_text(
            400, 300,
            text="📷 Upload images to start\n\nDrag and drop supported",
            font=('Segoe UI', 16),
            fill='#64748b',
            justify=tk.CENTER
        )
        
        # Navigation buttons
        self.nav_frame = tk.Frame(self.viewer_frame, bg=self.colors['light']['card'])
        self.nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.prev_btn = tk.Button(
            self.nav_frame,
            text="◀ Previous",
            font=('Segoe UI', 11),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text'],
            activebackground=self.colors['light']['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.prev_image
        )
        self.prev_btn.pack(side=tk.LEFT)
        
        self.image_info = tk.Label(
            self.nav_frame,
            text="No image selected",
            font=('Segoe UI', 11),
            bg=self.colors['light']['card'],
            fg=self.colors['light']['text_secondary']
        )
        self.image_info.pack(side=tk.LEFT, expand=True)
        
        self.next_btn = tk.Button(
            self.nav_frame,
            text="Next ▶",
            font=('Segoe UI', 11),
            bg=self.colors['light']['border'],
            fg=self.colors['light']['text'],
            activebackground=self.colors['light']['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.next_image
        )
        self.next_btn.pack(side=tk.RIGHT)
        
    def create_right_panel(self):
        """Create right panel with enhancement models"""
        self.right_panel = tk.Frame(
            self.content_frame,
            width=250,
            bg=self.colors['light']['sidebar'],
            highlightbackground=self.colors['light']['border'],
            highlightthickness=1
        )
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.right_panel.pack_propagate(False)
        
        # Models section
        self.models_section = tk.Frame(self.right_panel, bg=self.colors['light']['sidebar'])
        self.models_section.pack(fill=tk.X, padx=15, pady=15)
        
        self.models_title = tk.Label(
            self.models_section,
            text="🤖 Enhancement Models",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.models_title.pack(anchor=tk.W)
        
        self.models_subtitle = tk.Label(
            self.models_section,
            text="Select AI model for enhancement",
            font=('Segoe UI', 10),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary']
        )
        self.models_subtitle.pack(anchor=tk.W, pady=(5, 15))
        
        # Model buttons in matrix format
        self.models_frame = tk.Frame(self.models_section, bg=self.colors['light']['sidebar'])
        self.models_frame.pack(fill=tk.X)
        
        models = [
            ("A", "Matrix Format"),
            ("B", "Zero DCE"),
            ("C", "R1 Model"),
            ("D", "Deep Retinex"),
            ("E", "EnlightenGAN"),
            ("F", "SCI Model"),
            ("G", "URetinex-Net")
        ]
        
        self.model_buttons = {}
        for i, (letter, name) in enumerate(models):
            btn_frame = tk.Frame(
                self.models_frame,
                bg=self.colors['light']['sidebar'],
                highlightbackground=self.colors['light']['border'],
                highlightthickness=1
            )
            btn_frame.pack(fill=tk.X, pady=3)
            
            btn = tk.Button(
                btn_frame,
                text=f"{letter}. {name}",
                font=('Segoe UI', 11),
                bg=self.colors['light']['sidebar'],
                fg=self.colors['light']['text'],
                activebackground=self.colors['light']['accent'],
                activeforeground='white',
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor='hand2',
                anchor=tk.W,
                command=lambda l=letter, n=name: self.select_model(l, n)
            )
            btn.pack(fill=tk.X)
            self.model_buttons[letter] = btn
            
        # Highlight default model
        self.highlight_model("A")
        
        # Separator
        self.create_separator(self.right_panel)
        
        # Enhance button
        self.enhance_section = tk.Frame(self.right_panel, bg=self.colors['light']['sidebar'])
        self.enhance_section.pack(fill=tk.X, padx=15, pady=15)
        
        self.enhance_btn = tk.Button(
            self.enhance_section,
            text="✨ ENHANCE NOW",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['light']['accent'],
            fg='white',
            activebackground=self.colors['light']['accent_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor='hand2',
            command=self.enhance_images
        )
        self.enhance_btn.pack(fill=tk.X, pady=10)
        
        # Progress indicator
        self.progress_label = tk.Label(
            self.enhance_section,
            text="Ready to enhance",
            font=('Segoe UI', 10),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary']
        )
        self.progress_label.pack(pady=5)
        
        # Separator
        self.create_separator(self.right_panel)
        
        # Model info
        self.info_section = tk.Frame(self.right_panel, bg=self.colors['light']['sidebar'])
        self.info_section.pack(fill=tk.X, padx=15, pady=15)
        
        self.info_title = tk.Label(
            self.info_section,
            text="ℹ️ Model Info",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.info_title.pack(anchor=tk.W)
        
        self.info_text = tk.Label(
            self.info_section,
            text="Matrix Format: Advanced matrix-based\nimage enhancement algorithm\noptimized for low-light images.",
            font=('Segoe UI', 10),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary'],
            wraplength=220,
            justify=tk.LEFT
        )
        self.info_text.pack(anchor=tk.W, pady=10)
        
    def create_bottom_toolbar(self):
        """Create bottom toolbar with editing tools"""
        self.bottom_toolbar = tk.Frame(
            self.main_container,
            height=80,
            bg=self.colors['light']['sidebar'],
            highlightbackground=self.colors['light']['border'],
            highlightthickness=1
        )
        self.bottom_toolbar.pack(fill=tk.X, padx=10, pady=5)
        self.bottom_toolbar.pack_propagate(False)
        self.bottom_toolbar.lift()
        
        # Tools label
        self.tools_label = tk.Label(
            self.bottom_toolbar,
            text="🔧 Quick Tools:",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text']
        )
        self.tools_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Tool buttons
        tools = [
            ("📐 Resizing", self.open_resizing),
            ("✂️ Cropping", self.open_cropping),
            ("🔄 Data Augmentation", self.open_augmentation)
        ]
        
        for text, command in tools:
            btn = tk.Button(
                self.bottom_toolbar,
                text=text,
                font=('Segoe UI', 11),
                bg=self.colors['light']['border'],
                fg=self.colors['light']['text'],
                activebackground=self.colors['light']['accent'],
                activeforeground='white',
                relief=tk.FLAT,
                padx=20,
                pady=10,
                cursor='hand2',
                command=command
            )
            btn.pack(side=tk.LEFT, padx=10, pady=15)
            
        # Status indicator
        self.status_frame = tk.Frame(self.bottom_toolbar, bg=self.colors['light']['sidebar'])
        self.status_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=10,
            height=10,
            bg=self.colors['light']['sidebar'],
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_indicator.create_oval(0, 0, 10, 10, fill=self.colors['light']['success'])
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=('Segoe UI', 11),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text_secondary']
        )
        self.status_label.pack(side=tk.LEFT)
        
    def create_separator(self, parent):
        """Create a horizontal separator"""
        sep = tk.Frame(parent, height=1, bg=self.colors['light']['border'])
        sep.pack(fill=tk.X, padx=15, pady=10)
        
    # ==================== FUNCTIONALITY ====================
    
    def upload_images(self):
        """Upload multiple images"""
        filetypes = [
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp *.tiff'),
            ('All files', '*.*')
        ]
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=filetypes
        )
        
        if files:
            for file in files:
                if file not in self.uploaded_images:
                    self.uploaded_images.append(file)
                    self.add_image_to_list(file)
                    
            self.image_counter.config(text=f"{len(self.uploaded_images)} images uploaded")
            self.update_image_display()
            self.status_label.config(text="Images loaded")
            
    def add_image_to_list(self, filepath):
        """Add image to the list display"""
        filename = os.path.basename(filepath)
        img_frame = tk.Frame(
            self.image_list_frame,
            bg=self.colors['light']['sidebar'],
            highlightbackground=self.colors['light']['border'],
            highlightthickness=1
        )
        img_frame.pack(fill=tk.X, pady=2)
        
        label = tk.Label(
            img_frame,
            text=f"📷 {filename[:25]}{'...' if len(filename) > 25 else ''}",
            font=('Segoe UI', 9),
            bg=self.colors['light']['sidebar'],
            fg=self.colors['light']['text'],
            anchor=tk.W
        )
        label.pack(side=tk.LEFT, padx=5, pady=5)
        
        remove_btn = tk.Button(
            img_frame,
            text="✕",
            font=('Segoe UI', 8),
            bg=self.colors['light']['sidebar'],
            fg='#ef4444',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda f=filepath, fr=img_frame: self.remove_image(f, fr)
        )
        remove_btn.pack(side=tk.RIGHT, padx=5)
        
    def remove_image(self, filepath, frame):
        """Remove image from list"""
        if filepath in self.uploaded_images:
            self.uploaded_images.remove(filepath)
        frame.destroy()
        self.image_counter.config(text=f"{len(self.uploaded_images)} images uploaded")
        self.update_image_display()
        
    def choose_save_location(self):
        """Choose save folder location"""
        folder = filedialog.askdirectory(title="Select Save Location")
        if folder:
            self.save_path = folder
            display_path = folder if len(folder) < 35 else f"...{folder[-32:]}"
            self.path_display.config(text=display_path)
            
    def create_new_folder(self):
        """Create new folder for saving"""
        folder = filedialog.askdirectory(title="Select Parent Directory")
        if folder:
            new_folder_name = f"Enhanced_Images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            new_path = os.path.join(folder, new_folder_name)
            try:
                os.makedirs(new_path)
                self.save_path = new_path
                self.path_display.config(text=f"📁 {new_folder_name}")
                messagebox.showinfo("Success", f"Folder created:\n{new_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{str(e)}")
                
    def save_images(self):
        """Save enhanced images"""
        if not self.save_path:
            messagebox.showwarning("Warning", "Please select a save location first!")
            return
            
        if not self.enhanced_images:
            messagebox.showwarning("Warning", "No enhanced images to save!")
            return
            
        saved_count = 0
        for idx, img in self.enhanced_images.items():
            try:
                filename = f"enhanced_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(self.save_path, filename)
                img.save(filepath)
                saved_count += 1
            except Exception as e:
                print(f"Error saving image: {e}")
                
        messagebox.showinfo("Success", f"Saved {saved_count} images to:\n{self.save_path}")
        self.status_label.config(text=f"Saved {saved_count} images")
        
    def select_model(self, letter, name):
        """Select enhancement model"""
        self.selected_model.set(letter)
        self.highlight_model(letter)
        self.info_text.config(text=f"{name}: Advanced AI-powered\nimage enhancement model\nselected for processing.")
        self.status_label.config(text=f"Model {letter} selected")
        
    def highlight_model(self, letter):
        """Highlight selected model button"""
        theme = 'dark' if self.dark_mode.get() else 'light'
        for l, btn in self.model_buttons.items():
            if l == letter:
                btn.config(
                    bg=self.colors[theme]['accent'],
                    fg='white'
                )
            else:
                btn.config(
                    bg=self.colors[theme]['sidebar'],
                    fg=self.colors[theme]['text']
                )
                
    def enhance_images(self):
        """Enhance images with selected model"""
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Please upload images first!")
            return
            
        self.progress_label.config(text="Enhancing... Please wait")
        self.status_label.config(text="Processing...")
        self.enhance_btn.config(state=tk.DISABLED)
        
        # Run enhancement in separate thread
        thread = threading.Thread(target=self._enhance_thread)
        thread.start()
        
    def _enhance_thread(self):
        """Thread for image enhancement"""
        model = self.selected_model.get()
        
        for i, img_path in enumerate(self.uploaded_images):
            try:
                img = Image.open(img_path)
                
                # Apply different enhancements based on model
                if model == "A":  # Matrix Format
                    enhanced = self.apply_matrix_enhancement(img)
                elif model == "B":  # Zero DCE
                    enhanced = self.apply_zero_dce(img)
                elif model == "C":  # R1 Model
                    enhanced = self.apply_r1_model(img)
                else:
                    enhanced = self.apply_default_enhancement(img)
                    
                self.enhanced_images[i] = enhanced
                
                # Update UI
                self.after(0, lambda idx=i: self.update_progress(idx + 1))
                
            except Exception as e:
                print(f"Error enhancing image: {e}")
                
        self.after(0, self.enhancement_complete)
        
    def apply_matrix_enhancement(self, img):
        """Matrix format enhancement"""
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Enhance brightness and contrast
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        return img
        
    def apply_zero_dce(self, img):
        """Zero DCE style enhancement"""
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Simulated Zero DCE enhancement
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.4)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Color balance
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.1)))
        img = Image.merge('RGB', (r, g, b))
        
        return img
        
    def apply_r1_model(self, img):
        """R1 model enhancement"""
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.4)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
        
        return img
        
    def apply_default_enhancement(self, img):
        """Default enhancement"""
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.15)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        return img
        
    def update_progress(self, count):
        """Update progress label"""
        self.progress_label.config(text=f"Enhanced {count}/{len(self.uploaded_images)} images")
        
    def enhancement_complete(self):
        """Called when enhancement is complete"""
        self.progress_label.config(text="Enhancement complete!")
        self.status_label.config(text="Ready")
        self.enhance_btn.config(state=tk.NORMAL)
        self.update_image_display()
        messagebox.showinfo("Success", "Images enhanced successfully!")
        
    def update_image_display(self):
        """Update the image display"""
        if not self.uploaded_images:
            self.image_canvas.delete("all")
            self.placeholder_text = self.image_canvas.create_text(
                300, 200,
                text="📷 Upload images to start\n\nDrag and drop supported",
                font=('Segoe UI', 16),
                fill='#64748b',
                justify=tk.CENTER
            )
            self.image_info.config(text="No image selected")
            return
            
        # Display current image
        try:
            img_path = self.uploaded_images[self.current_image_index]
            img = Image.open(img_path)
            
            # Resize for display
            canvas_width = max(self.image_canvas.winfo_width() - 40, 100)
            canvas_height = max(self.image_canvas.winfo_height() - 40, 100)
            
            if canvas_width > 100 and canvas_height > 100:
                img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
            self.current_photo = ImageTk.PhotoImage(img)
            
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                canvas_width // 2 + 20,
                canvas_height // 2 + 20,
                image=self.current_photo,
                anchor=tk.CENTER
            )
            
            filename = os.path.basename(img_path)
            self.image_info.config(text=f"{self.current_image_index + 1}/{len(self.uploaded_images)}: {filename[:30]}")
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            
    def prev_image(self):
        """Show previous image"""
        if self.uploaded_images:
            self.current_image_index = (self.current_image_index - 1) % len(self.uploaded_images)
            self.update_image_display()
            
    def next_image(self):
        """Show next image"""
        if self.uploaded_images:
            self.current_image_index = (self.current_image_index + 1) % len(self.uploaded_images)
            self.update_image_display()
            
    def toggle_comparison(self):
        """Toggle side-by-side comparison"""
        if self.compare_var.get():
            messagebox.showinfo("Compare Mode", "Side-by-side comparison enabled!")
        
    def open_resizing(self):
        """Open resizing dialog"""
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Please upload images first!")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Resizing Tool")
        dialog.geometry("400x300")
        dialog.transient(self)
        
        tk.Label(
            dialog,
            text="📐 Image Resizing",
            font=('Segoe UI', 16, 'bold')
        ).pack(pady=20)
        
        # Width input
        width_frame = tk.Frame(dialog)
        width_frame.pack(pady=10)
        
        tk.Label(width_frame, text="Width:", font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=10)
        width_entry = tk.Entry(width_frame, font=('Segoe UI', 12), width=10)
        width_entry.pack(side=tk.LEFT)
        width_entry.insert(0, "800")
        tk.Label(width_frame, text="px", font=('Segoe UI', 12)).pack(side=tk.LEFT)
        
        # Height input
        height_frame = tk.Frame(dialog)
        height_frame.pack(pady=10)
        
        tk.Label(height_frame, text="Height:", font=('Segoe UI', 12)).pack(side=tk.LEFT, padx=10)
        height_entry = tk.Entry(height_frame, font=('Segoe UI', 12), width=10)
        height_entry.pack(side=tk.LEFT)
        height_entry.insert(0, "600")
        tk.Label(height_frame, text="px", font=('Segoe UI', 12)).pack(side=tk.LEFT)
        
        # Maintain aspect ratio
        maintain_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            dialog,
            text="Maintain aspect ratio",
            variable=maintain_var,
            font=('Segoe UI', 11)
        ).pack(pady=10)
        
        # Apply button
        tk.Button(
            dialog,
            text="Apply Resize",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=dialog.destroy
        ).pack(pady=20)
        
    def open_cropping(self):
        """Open cropping dialog"""
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Please upload images first!")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Cropping Tool")
        dialog.geometry("400x350")
        dialog.transient(self)
        
        tk.Label(
            dialog,
            text="✂️ Image Cropping",
            font=('Segoe UI', 16, 'bold')
        ).pack(pady=20)
        
        # Preset ratios
        tk.Label(dialog, text="Aspect Ratio Presets:", font=('Segoe UI', 12)).pack(pady=10)
        
        ratios_frame = tk.Frame(dialog)
        ratios_frame.pack(pady=5)
        
        ratios = [("1:1", "Square"), ("16:9", "Widescreen"), ("4:3", "Standard"), ("3:2", "Photo")]
        for ratio, name in ratios:
            tk.Button(
                ratios_frame,
                text=f"{ratio}\n{name}",
                font=('Segoe UI', 10),
                width=10,
                relief=tk.FLAT,
                bg=self.colors['light']['border']
            ).pack(side=tk.LEFT, padx=5)
            
        # Custom dimensions
        custom_frame = tk.Frame(dialog)
        custom_frame.pack(pady=20)
        
        tk.Label(custom_frame, text="Custom:", font=('Segoe UI', 12)).pack(anchor=tk.W)
        
        dims_frame = tk.Frame(custom_frame)
        dims_frame.pack(pady=5)
        
        tk.Label(dims_frame, text="X:", font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=5)
        tk.Entry(dims_frame, font=('Segoe UI', 11), width=6).pack(side=tk.LEFT)
        tk.Label(dims_frame, text="Y:", font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=5)
        tk.Entry(dims_frame, font=('Segoe UI', 11), width=6).pack(side=tk.LEFT)
        tk.Label(dims_frame, text="W:", font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=5)
        tk.Entry(dims_frame, font=('Segoe UI', 11), width=6).pack(side=tk.LEFT)
        tk.Label(dims_frame, text="H:", font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=5)
        tk.Entry(dims_frame, font=('Segoe UI', 11), width=6).pack(side=tk.LEFT)
        
        # Apply button
        tk.Button(
            dialog,
            text="Apply Crop",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=dialog.destroy
        ).pack(pady=20)
        
    def open_augmentation(self):
        """Open data augmentation dialog"""
        if not self.uploaded_images:
            messagebox.showwarning("Warning", "Please upload images first!")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Data Augmentation")
        dialog.geometry("450x400")
        dialog.transient(self)
        
        tk.Label(
            dialog,
            text="🔄 Data Augmentation",
            font=('Segoe UI', 16, 'bold')
        ).pack(pady=20)
        
        # Augmentation options
        options_frame = tk.Frame(dialog)
        options_frame.pack(pady=10, padx=30, fill=tk.X)
        
        augmentations = [
            ("Horizontal Flip", True),
            ("Vertical Flip", False),
            ("Random Rotation", True),
            ("Brightness Adjustment", True),
            ("Noise Addition", False),
            ("Blur Effect", False),
            ("Color Jitter", True)
        ]
        
        self.aug_vars = {}
        for aug, default in augmentations:
            var = tk.BooleanVar(value=default)
            self.aug_vars[aug] = var
            tk.Checkbutton(
                options_frame,
                text=aug,
                variable=var,
                font=('Segoe UI', 11),
                anchor=tk.W
            ).pack(fill=tk.X, pady=3)
            
        # Number of augmented images
        count_frame = tk.Frame(dialog)
        count_frame.pack(pady=15)
        
        tk.Label(count_frame, text="Number of variations per image:", font=('Segoe UI', 11)).pack(side=tk.LEFT)
        count_spin = tk.Spinbox(count_frame, from_=1, to=10, width=5, font=('Segoe UI', 11))
        count_spin.pack(side=tk.LEFT, padx=10)
        count_spin.delete(0, tk.END)
        count_spin.insert(0, "3")
        
        # Apply button
        tk.Button(
            dialog,
            text="Generate Augmented Data",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light']['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=dialog.destroy
        ).pack(pady=20)
        
    def toggle_gpu(self):
        """Toggle GPU processing"""
        self.gpu_enabled.set(not self.gpu_enabled.get())
        
        if self.gpu_enabled.get():
            self.gpu_btn.config(
                bg=self.colors['light']['gpu_glow'],
                text="GPU Processing ON"
            )
            self.gpu_indicator.itemconfig('indicator', fill='#22d3ee')
            self.status_label.config(text="GPU Mode Active - UI Alive!")
            self.animation_active = True
            self.start_gpu_animation()
        else:
            theme = 'dark' if self.dark_mode.get() else 'light'
            self.gpu_btn.config(
                bg=self.colors[theme]['border'],
                text="GPU Processing"
            )
            self.gpu_indicator.itemconfig('indicator', fill='#94a3b8')
            self.status_label.config(text="CPU Mode Active")
            self.animation_active = False
            self.stop_gpu_animation()
            
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        self.dark_mode.set(not self.dark_mode.get())
        self.apply_theme()
        
    def apply_theme(self):
        """Apply current theme to all widgets"""
        theme = 'dark' if self.dark_mode.get() else 'light'
        colors = self.colors[theme]
        
        # Update theme button
        if self.dark_mode.get():
            self.theme_btn.config(text="☀️ Light Mode")
        else:
            self.theme_btn.config(text="🌙 Dark Mode")
            
        # Update main container
        self.main_container.config(bg=colors['bg'])
        self.content_frame.config(bg=colors['bg'])
        
        # Update header
        self.header.config(bg=colors['sidebar'])
        self.logo_frame.config(bg=colors['sidebar'])
        self.logo_label.config(bg=colors['sidebar'], fg=colors['accent'])
        self.title_label.config(bg=colors['sidebar'], fg=colors['text'])
        self.version_label.config(bg=colors['accent'])
        self.controls_frame.config(bg=colors['sidebar'])
        
        if not self.gpu_enabled.get():
            self.gpu_btn.config(bg=colors['border'], fg=colors['text'])
        self.gpu_frame.config(bg=colors['sidebar'])
        self.gpu_indicator.config(bg=colors['sidebar'])
        self.theme_btn.config(bg=colors['border'], fg=colors['text'])
        
        # Update left sidebar
        self.left_sidebar.config(bg=colors['sidebar'], highlightbackground=colors['border'])
        self.upload_section.config(bg=colors['sidebar'])
        self.upload_title.config(bg=colors['sidebar'], fg=colors['text'])
        self.upload_subtitle.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        self.upload_btn.config(bg=colors['accent'])
        self.image_counter.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        
        self.save_section.config(bg=colors['sidebar'])
        self.save_title.config(bg=colors['sidebar'], fg=colors['text'])
        self.path_frame.config(bg=colors['sidebar'])
        self.path_label.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        self.path_display.config(bg=colors['border'], fg=colors['text_secondary'])
        self.browse_btn.config(bg=colors['border'], fg=colors['text'])
        self.new_folder_btn.config(bg=colors['border'], fg=colors['text'])
        
        self.list_section.config(bg=colors['sidebar'])
        self.list_title.config(bg=colors['sidebar'], fg=colors['text'])
        self.list_canvas.config(bg=colors['sidebar'])
        self.image_list_frame.config(bg=colors['sidebar'])
        
        # Update center panel
        self.center_panel.config(bg=colors['bg'])
        self.viewer_frame.config(bg=colors['card'], highlightbackground=colors['border'])
        self.viewer_header.config(bg=colors['card'])
        self.viewer_title.config(bg=colors['card'], fg=colors['text'])
        self.compare_check.config(bg=colors['card'], fg=colors['text'], selectcolor=colors['accent'])
        self.nav_frame.config(bg=colors['card'])
        self.prev_btn.config(bg=colors['border'], fg=colors['text'])
        self.image_info.config(bg=colors['card'], fg=colors['text_secondary'])
        self.next_btn.config(bg=colors['border'], fg=colors['text'])
        
        # Update right panel
        self.right_panel.config(bg=colors['sidebar'], highlightbackground=colors['border'])
        self.models_section.config(bg=colors['sidebar'])
        self.models_title.config(bg=colors['sidebar'], fg=colors['text'])
        self.models_subtitle.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        self.models_frame.config(bg=colors['sidebar'])
        
        self.highlight_model(self.selected_model.get())
        
        self.enhance_section.config(bg=colors['sidebar'])
        self.enhance_btn.config(bg=colors['accent'])
        self.progress_label.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        
        self.info_section.config(bg=colors['sidebar'])
        self.info_title.config(bg=colors['sidebar'], fg=colors['text'])
        self.info_text.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        
        # Update bottom toolbar
        self.bottom_toolbar.config(bg=colors['sidebar'], highlightbackground=colors['border'])
        self.tools_label.config(bg=colors['sidebar'], fg=colors['text'])
        self.status_frame.config(bg=colors['sidebar'])
        self.status_label.config(bg=colors['sidebar'], fg=colors['text_secondary'])
        self.status_indicator.config(bg=colors['sidebar'])
        
    def start_animations(self):
        """Start UI animations"""
        self.animate_logo()
        
    def animate_logo(self):
        """Animate the logo"""
        colors = ['#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e', '#6366f1']
        if hasattr(self, '_logo_color_idx'):
            self._logo_color_idx = (self._logo_color_idx + 1) % len(colors)
        else:
            self._logo_color_idx = 0
        self.logo_label.config(fg=colors[self._logo_color_idx])
        self.after(1000, self.animate_logo)
        
    def start_gpu_animation(self):
        """Start GPU mode animations - make UI come alive"""
        self.animate_gpu_glow()
        self.create_particles()
        
    def stop_gpu_animation(self):
        """Stop GPU mode animations"""
        self.bg_canvas.delete('particle')
        self.bg_canvas.delete('glow')
        self.particles = []
        
    def animate_gpu_glow(self):
        """Animate GPU button glow"""
        if not self.gpu_enabled.get():
            return
            
        # Pulsing glow effect
        self.glow_intensity += self.glow_direction * 5
        if self.glow_intensity >= 100:
            self.glow_direction = -1
        elif self.glow_intensity <= 20:
            self.glow_direction = 1
            
        # Update GPU button with glow
        intensity = hex(self.glow_intensity)[2:].zfill(2)
        glow_color = f'#22d3ee{intensity}'
        
        self.after(50, self.animate_gpu_glow)
        
    def create_particles(self):
        """Create animated particles for GPU mode"""
        if not self.gpu_enabled.get():
            return
            
        # Create floating particles
        width = self.winfo_width()
        height = self.winfo_height()
        
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 8)
            
            particle = self.bg_canvas.create_oval(
                x, y, x + size, y + size,
                fill='#22d3ee',
                outline='',
                tags='particle',
                stipple='gray50'
            )
            self.particles.append({
                'id': particle,
                'x': x,
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': size
            })
            
        self.animate_particles()
        
    def animate_particles(self):
        """Animate floating particles"""
        if not self.gpu_enabled.get():
            return
            
        width = self.winfo_width()
        height = self.winfo_height()
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            # Bounce off edges
            if p['x'] < 0 or p['x'] > width:
                p['vx'] *= -1
            if p['y'] < 0 or p['y'] > height:
                p['vy'] *= -1
                
            self.bg_canvas.coords(
                p['id'],
                p['x'], p['y'],
                p['x'] + p['size'], p['y'] + p['size']
            )
            
        self.after(30, self.animate_particles)

# Run the application
if __name__ == "__main__":
    app = ImageEnhancerPro()
    app.mainloop()
