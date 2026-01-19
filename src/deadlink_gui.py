#!/usr/bin/env python3
"""
Dead Link Checker - Desktop GUI Application
A modern, professional desktop application for checking dead links on websites.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import queue
from datetime import datetime
import os
from pathlib import Path
import webbrowser
from PIL import Image
import pystray
from pystray import MenuItem as item
from plyer import notification
from CTkTable import *

# Import the core functionality from deadlink_checker
# Import the core functionality from the modular deadlink package
from deadlink import (
    setup_windows_encoding,
    open_file,
    check_all_links, 
    generate_report, 
    save_report, 
    generate_pdf_report,
    generate_csv_report,
    get_report_filename,
    LinkResult,
    DatabaseManager,
    VERSION
)

import json

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "workers": 10,
    "depth": 1,
    "timeout": 10,
    "report_dir": "reports",
    "generate_txt": True,
    "generate_pdf": True,
    "generate_csv": True,
    "user_agent": "Default",
    "auth_type": "None",
    "username": "",
    "password": "",
    "cookies": "",
    "exclude_rules": "",
    "check_external": True
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults for missing keys
                return {**DEFAULT_CONFIG, **config}
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except:
        pass


class DeadLinkCheckerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Dead Link Checker - Website Analysis Tool")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set window icon (if available)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Load configuration
        self.config = load_config()
        
        # Initialize variables
        self.is_checking = False
        self.is_paused = False
        self.results = []
        self.current_url = ""
        self.progress_queue = queue.Queue()
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.db = DatabaseManager()
        self.tray_icon = None
        
        # Create UI
        self.create_widgets()
        
        # Schedule deferred initialization to keep startup snappy
        # Use a small delay to let the main window render first
        self.after(100, self.setup_tray)
        self.after(200, self.monitor_progress)
        
        # Protocol
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # ==================== HEADER ====================
        header_frame = ctk.CTkFrame(self, fg_color=("#1a5276", "#0d2840"), corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Left side - Title & Subtitle container
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, rowspan=2, pady=15, padx=20, sticky="w")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🔗 DEAD LINK CHECKER",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="  |  Professional Website Link Analysis & Reporting Tool",
            font=ctk.CTkFont(size=12),
            text_color="#a8d5ff"
        )
        subtitle_label.pack(side="left", padx=(5, 0), pady=(5, 0))

        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, padx=20, pady=(15, 0), sticky="ne")

        # History Button
        self.history_button = ctk.CTkButton(
            button_frame,
            text="📜 History",
            width=90,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#1d8348",
            hover_color="#186a3b",
            command=self.open_history
        )
        self.history_button.pack(side="left", padx=(0, 10))

        # Settings Button
        self.settings_button = ctk.CTkButton(
            button_frame,
            text="⚙️ Settings",
            width=90,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.open_settings
        )
        self.settings_button.pack(side="left")
        
        # Right side - Version, Copyright, Owner (Compact)
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.grid(row=1, column=1, pady=(0, 15), padx=20, sticky="e")
        
        line1_label = ctk.CTkLabel(
            info_frame,
            text=f"Version {VERSION} | Copy 2026 All Rights Reserved",
            font=ctk.CTkFont(size=11),
            text_color="#a8d5ff"
        )
        line1_label.pack(anchor="e")
        
        line2_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        line2_frame.pack(anchor="e")
        
        owner_label = ctk.CTkLabel(
            line2_frame,
            text="arif98741 | ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff"
        )
        owner_label.pack(side="left")
        
        website_label = ctk.CTkLabel(
            line2_frame,
            text="Devtobox.com",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#4da6ff",
            cursor="hand2"
        )
        website_label.pack(side="left")
        website_label.bind("<Button-1>", lambda e: webbrowser.open("https://devtobox.com"))
        
        # ==================== LEFT PANEL - CONTROLS ====================
        left_panel = ctk.CTkScrollableFrame(self, corner_radius=10)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=400)
        self.grid_columnconfigure(1, weight=1)
        
        # Analysis Mode Section
        mode_label = ctk.CTkLabel(
            left_panel,
            text="Analysis Mode",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        mode_label.pack(pady=(20, 5), padx=20, anchor="w")

        self.analysis_mode = ctk.StringVar(value="recursive")
        
        mode_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        mode_frame.pack(pady=5, padx=20, fill="x")
        
        self.web_mode_radio = ctk.CTkRadioButton(
            mode_frame, text="Website Crawler", 
            variable=self.analysis_mode, value="recursive",
            command=self.on_mode_change
        )
        self.web_mode_radio.pack(side="left", padx=(0, 20))
        
        self.sitemap_mode_radio = ctk.CTkRadioButton(
            mode_frame, text="Sitemap.xml", 
            variable=self.analysis_mode, value="sitemap",
            command=self.on_mode_change
        )
        self.sitemap_mode_radio.pack(side="left")

        # URL Input Section
        self.url_label = ctk.CTkLabel(
            left_panel,
            text="Target Website URL",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.url_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.url_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text="https://example.com/sitemap.xml",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(pady=(0, 20), padx=20, fill="x")
        
        # Settings Section
        settings_label = ctk.CTkLabel(
            left_panel,
            text="Analysis Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.pack(pady=(10, 10), padx=20, anchor="w")
        
        # Crawl Depth
        depth_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        depth_frame.pack(pady=5, padx=20, fill="x")
        
        depth_label = ctk.CTkLabel(
            depth_frame,
            text="Crawl Depth:",
            font=ctk.CTkFont(size=13)
        )
        depth_label.pack(side="left", padx=(0, 10))
        
        self.depth_slider = ctk.CTkSlider(
            depth_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=self.update_depth_label
        )
        self.depth_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.depth_slider.set(self.config.get("depth", 1))
        
        self.depth_value_label = ctk.CTkLabel(
            depth_frame,
            text=str(int(self.config.get("depth", 1))),
            font=ctk.CTkFont(size=13, weight="bold"),
            width=30
        )
        self.depth_value_label.pack(side="left", padx=(5, 0))
        
        depth_info = ctk.CTkLabel(
            left_panel,
            text="1 = Homepage only, 2+ = Follow internal links",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        depth_info.pack(pady=(0, 10), padx=20, anchor="w")

        # Check External Links
        self.check_external = ctk.CTkCheckBox(
            left_panel,
            text="Check External Links",
            font=ctk.CTkFont(size=13)
        )
        self.check_external.pack(pady=(5, 10), padx=20, anchor="w")
        if self.config.get("check_external", True):
            self.check_external.select()
        else:
            self.check_external.deselect()
        
        # Workers
        workers_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        workers_frame.pack(pady=5, padx=20, fill="x")
        
        workers_label = ctk.CTkLabel(
            workers_frame,
            text="Concurrent Workers:",
            font=ctk.CTkFont(size=13)
        )
        workers_label.pack(side="left", padx=(0, 10))
        
        self.workers_slider = ctk.CTkSlider(
            workers_frame,
            from_=5,
            to=50,
            number_of_steps=9,
            command=self.update_workers_label
        )
        self.workers_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.workers_slider.set(self.config.get("workers", 10))
        
        self.workers_value_label = ctk.CTkLabel(
            workers_frame,
            text=str(int(self.config.get("workers", 10))),
            font=ctk.CTkFont(size=13, weight="bold"),
            width=30
        )
        self.workers_value_label.pack(side="left", padx=(5, 0))

        
        # Timeout
        timeout_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        timeout_frame.pack(pady=5, padx=20, fill="x")
        
        timeout_label = ctk.CTkLabel(
            timeout_frame,
            text="Timeout (seconds):",
            font=ctk.CTkFont(size=13)
        )
        timeout_label.pack(side="left", padx=(0, 10))
        
        self.timeout_slider = ctk.CTkSlider(
            timeout_frame,
            from_=5,
            to=30,
            number_of_steps=5,
            command=self.update_timeout_label
        )
        self.timeout_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.timeout_slider.set(self.config.get("timeout", 10))
        
        self.timeout_value_label = ctk.CTkLabel(
            timeout_frame,
            text=f"{int(self.config.get('timeout', 10))}s",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=30
        )
        self.timeout_value_label.pack(side="left", padx=(5, 0))
        
        # Report Options
        report_label = ctk.CTkLabel(
            left_panel,
            text="Report Options",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        report_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        self.generate_txt = ctk.CTkCheckBox(
            left_panel,
            text="Generate Text Report (.txt)",
            font=ctk.CTkFont(size=13)
        )
        self.generate_txt.pack(pady=5, padx=20, anchor="w")
        if self.config.get("generate_txt", True):
            self.generate_txt.select()
        else:
            self.generate_txt.deselect()
        
        self.generate_pdf = ctk.CTkCheckBox(
            left_panel,
            text="Generate PDF Report (.pdf)",
            font=ctk.CTkFont(size=13)
        )
        self.generate_pdf.pack(pady=5, padx=20, anchor="w")
        if self.config.get("generate_pdf", True):
            self.generate_pdf.select()
        else:
            self.generate_pdf.deselect()
        
        self.generate_csv = ctk.CTkCheckBox(
            left_panel,
            text="Generate CSV Report (.csv)",
            font=ctk.CTkFont(size=13)
        )
        self.generate_csv.pack(pady=5, padx=20, anchor="w")
        if self.config.get("generate_csv", True):
            self.generate_csv.select()
        else:
            self.generate_csv.deselect()
        
        # Action Buttons
        button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        button_frame.pack(pady=30, padx=20, fill="x")
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start",
            command=self.start_check,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#27ae60", "#1e8449"),
            hover_color=("#2ecc71", "#27ae60"),
            corner_radius=8
        )
        self.start_button.pack(fill="x", pady=5)
        
        # Stop and Pause in a horizontal frame for a more compact/premium redesign
        control_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        control_frame.pack(fill="x", pady=0)
        control_frame.grid_columnconfigure((0, 1), weight=1)

        self.pause_button = ctk.CTkButton(
            control_frame,
            text="⏸ Pause",
            command=self.toggle_pause,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#f39c12", "#d35400"),
            hover_color=("#f1c40f", "#f39c12"),
            state="disabled",
            corner_radius=8
        )
        self.pause_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.stop_button = ctk.CTkButton(
            control_frame,
            text="⏹ Stop",
            command=self.stop_check,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#c0392b", "#922b21"),
            hover_color=("#e74c3c", "#c0392b"),
            state="disabled",
            corner_radius=8
        )
        self.stop_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        # ==================== RIGHT PANEL - RESULTS ====================
        right_panel = ctk.CTkFrame(self, corner_radius=10)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Results Header
        results_header = ctk.CTkLabel(
            right_panel,
            text="Analysis Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_header.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(right_panel)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.progress_bar.set(0)

        # Interactive Results Grid (replacing text area or adding alongside)
        # We will use a TabView to switch between Log and Table
        self.tab_view = ctk.CTkTabview(right_panel)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.tab_view.add("Log View")
        self.tab_view.add("Grid View")
        self.tab_view.set("Grid View") # Set Grid View as default
        
        self.status_text = ctk.CTkTextbox(
            self.tab_view.tab("Log View"),
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.status_text.pack(fill="both", expand=True)
        
        # Grid View
        self.grid_frame = ctk.CTkFrame(self.tab_view.tab("Grid View"))
        self.grid_frame.pack(fill="both", expand=True)
        
        # Search/Filter in Grid
        filter_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=5, padx=5)
        
        self.grid_search = ctk.CTkEntry(filter_frame, placeholder_text="Filter results...", height=30)
        self.grid_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.grid_search.bind("<KeyRelease>", self.filter_grid)
        
        self.grid_table_container = ctk.CTkScrollableFrame(self.grid_frame)
        self.grid_table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.table = None # Will be initialized on first result
        
        # Statistics Frame
        stats_frame = ctk.CTkFrame(right_panel)
        stats_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stat Cards
        self.total_label = self.create_stat_card(stats_frame, "Total Links", "0", 0)
        self.working_label = self.create_stat_card(stats_frame, "Working", "0", 1, "#27ae60")
        self.broken_label = self.create_stat_card(stats_frame, "Broken", "0", 2, "#c0392b")
        self.success_label = self.create_stat_card(stats_frame, "Success Rate", "0%", 3, "#2980b9")
        
        # Action Buttons for Results
        action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        action_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(10, 20))
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.open_reports_button = ctk.CTkButton(
            action_frame,
            text="📁 Open Reports Folder",
            command=self.open_reports_folder,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.open_reports_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.clear_button = ctk.CTkButton(
            action_frame,
            text="🗑️ Clear Results",
            command=self.clear_results,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="gray40",
            hover_color="gray30"
        )
        self.clear_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Initial welcome message
        self.show_welcome_message()
    
    def on_mode_change(self):
        """Handle change in analysis mode"""
        mode = self.analysis_mode.get()
        if mode == "sitemap":
            self.url_label.configure(text="Sitemap URL (.xml)")
            self.url_entry.configure(placeholder_text="https://example.com/sitemap.xml")
            self.depth_slider.configure(state="disabled")
            self.depth_slider.set(1)
            self.update_depth_label(1)
        else:
            self.url_label.configure(text="Target Website URL")
            self.url_entry.configure(placeholder_text="https://example.com")
            self.depth_slider.configure(state="normal")

    def open_history(self):
        """Open the report history window"""
        HistoryWindow(self)

    def open_settings(self):
        """Open the settings window"""
        SettingsWindow(self)

    
    def create_stat_card(self, parent, title, value, column, color="#2980b9"):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=column, padx=5, pady=10, sticky="ew")
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=(10, 0))
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        title_label.pack(pady=(0, 10))
        
        return value_label
    
    def show_welcome_message(self):
        """Display welcome message"""
        welcome = f"""
╔══════════════════════════════════════════════════════════════╗
║           Welcome to Dead Link Checker v{VERSION}                  ║
╚══════════════════════════════════════════════════════════════╝

📋 How to use:
  1. Enter the website URL you want to analyze
  2. Configure analysis settings (depth, workers, timeout)
  3. Select report formats (TXT and/or PDF)
  4. Click "Start Analysis" to begin
  
💡 Tips:
  • Crawl Depth 1: Checks only the homepage links
  • Crawl Depth 2+: Follows internal links recursively
  • Higher workers = faster analysis (but more resource intensive)
  • Reports are automatically saved in the 'reports' folder
  
🚀 Ready to start? Enter a URL above and click "Start Analysis"!
        """
        self.status_text.insert("1.0", welcome)
        self.status_text.configure(state="disabled")
    
    def update_depth_label(self, value):
        """Update depth label"""
        self.depth_value_label.configure(text=str(int(float(value))))
    
    def update_workers_label(self, value):
        """Update workers label"""
        self.workers_value_label.configure(text=str(int(float(value))))
    
    def update_timeout_label(self, value):
        """Update timeout label"""
        self.timeout_value_label.configure(text=f"{int(float(value))}s")
    
    def start_check(self):
        """Start the link checking process"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL to check!")
            return
        
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, url)
        
        # Get settings
        depth = int(float(self.depth_slider.get()))
        workers = int(float(self.workers_slider.get()))
        timeout = int(float(self.timeout_slider.get()))
        check_ext = self.check_external.get()
        
        # Update UI state
        self.is_checking = True
        self.is_paused = False
        self.current_url = url
        self.pause_event.clear()
        self.stop_event.clear()
        
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.pause_button.configure(state="normal", text="⏸ Pause")
        self.url_entry.configure(state="disabled")
        
        # Clear previous results
        self.results = []
        if self.table:
            self.table.destroy()
            self.table = None
        
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.configure(state="disabled")
        self.progress_bar.set(0)
        
        # Start checking in a separate thread
        thread = threading.Thread(
            target=self.check_links_thread,
            args=(url, depth, workers, timeout, check_ext),
            daemon=True
        )
        thread.start()
    
    def get_headers_and_auth(self):
        """Prepare headers and auth from configuration."""
        headers = {}
        
        # User Agent
        ua_map = {
            "Default": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "iPhone (iOS 15)": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Android (Chrome)": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
        }
        ua_choice = self.config.get("user_agent", "Default")
        headers['User-Agent'] = ua_map.get(ua_choice, ua_map["Default"])
        
        # Cookies
        cookies = self.config.get("cookies", "").strip()
        if cookies:
            headers['Cookie'] = cookies
            
        # Auth
        auth = None
        if self.config.get("auth_type") == "Basic":
            user = self.config.get("username", "")
            pw = self.config.get("password", "")
            if user or pw:
                auth = (user, pw)
                
        return headers, auth

    def check_links_thread(self, url, depth, workers, timeout, check_external=True):
        """Thread function to check links"""
        headers, auth = self.get_headers_and_auth()
        try:
            mode = self.analysis_mode.get()
            self.log_message(f"🚀 Starting {mode} analysis of: {url}\n")
            self.log_message(f"⚙️  Settings: Workers={workers}, Timeout={timeout}s" + (f", Depth={depth}" if mode != "sitemap" else "") + "\n")
            
            if self.config.get("auth_type") == "Basic":
                self.log_message(f"🔑 Authentication using: Basic Auth\n")
            if self.config.get("user_agent") != "Default":
                self.log_message(f"👤 Identity: {self.config.get('user_agent')}\n")
            if self.config.get("cookies"):
                self.log_message(f"🍪 Session Cookies applied\n")
                
            self.log_message("=" * 60 + "\n\n")
            
            headers, auth = self.get_headers_and_auth()
            exclude_patterns = [p.strip() for p in self.config.get("exclude_rules", "").split('\n') if p.strip()]
            
            # Check links with progress callback
            results = check_all_links(
                url, 
                max_workers=workers, 
                timeout=timeout, 
                max_depth=depth, 
                progress_callback=self.log_message,
                auth=auth,
                headers=headers,
                exclude_patterns=exclude_patterns,
                pause_event=self.pause_event,
                stop_event=self.stop_event,
                check_external=check_external
            )
            
            if self.stop_event.is_set():
                self.log_message("\n⚠️  Analysis stopped by user.\n")
                self.show_notification("Analysis Stopped", f"The analysis for {url} was stopped.")
                return
            
            self.show_notification("Analysis Complete", f"Found {len(results)} links on {url}.")
            
            self.results = results
            
            # Generate report
            self.log_message("\n" + "=" * 60 + "\n")
            self.log_message("📊 Generating reports...\n\n")
            
            report = generate_report(results)
            self.log_message(report + "\n")
            
            # Save reports
            report_dir = self.config.get("report_dir", "reports")
            from datetime import datetime
            session_folder = f"report_{datetime.now().strftime('%y_%m_%d_%H%M%S')}"
            
            if self.generate_txt.get():
                txt_filename = get_report_filename(url, "txt", report_dir, session_folder)
                save_report(report, txt_filename)
                self.log_message(f"\n✅ Text report saved: {txt_filename}\n")
            
            if self.generate_pdf.get():
                pdf_filename = get_report_filename(url, "pdf", report_dir, session_folder)
                generate_pdf_report(results, pdf_filename, url)
                self.log_message(f"✅ PDF report saved: {pdf_filename}\n")
            
            if self.generate_csv.get():
                csv_filename = get_report_filename(url, "csv", report_dir, session_folder)
                generate_csv_report(results, csv_filename, url)
                self.log_message(f"✅ CSV report saved: {csv_filename}\n")
            
            # Save to Database
            self.db.save_session(url, mode, results, session_folder)
            
            # Update statistics
            self.update_statistics(results)
            
            self.log_message("\n🎉 Analysis complete and saved to history!\n")
            
        except Exception as e:
            self.log_message(f"\n❌ Error: {str(e)}\n")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.is_checking = False
            self.after(0, self.reset_ui)
    
    def stop_check(self):
        """Stop the checking process"""
        self.is_checking = False
        self.stop_event.set()
        self.pause_event.clear()
        self.log_message("\n⏹ Stopping analysis...\n")
        self.reset_ui()
    
    def toggle_pause(self):
        """Toggle pause/resume"""
        if not self.is_checking:
            return
            
        if not self.is_paused:
            self.is_paused = True
            self.pause_event.set()
            self.pause_button.configure(text="▶ Resume", fg_color=("#27ae60", "#1e8449"), hover_color=("#2ecc71", "#27ae60"))
            self.log_message("\n⏸ Analysis paused.\n")
        else:
            self.is_paused = False
            self.pause_event.clear()
            self.pause_button.configure(text="⏸ Pause", fg_color=("#f39c12", "#d35400"), hover_color=("#f1c40f", "#f39c12"))
            self.log_message("\n▶ Analysis resumed.\n")

    def setup_tray(self):
        """Setup system tray icon"""
        def init_tray():
            try:
                # Use a default icon if assets/icon.png is missing
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                else:
                    image = Image.new('RGB', (64, 64), color=(0, 120, 215))
                
                menu = (
                    item('Restore', self.show_window),
                    item('Exit', self.exit_app)
                )
                self.tray_icon = pystray.Icon("deadlinkchecker", image, "Dead Link Checker", menu)
                self.tray_icon.run()
            except Exception as e:
                print(f"Tray error: {e}")

        # Run tray initialization in a separate thread to avoid blocking startup
        threading.Thread(target=init_tray, daemon=True).start()

    def show_window(self):
        """Show the main window from tray"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def exit_app(self):
        """Exit the application completely"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.quit()

    def show_notification(self, title, message):
        """Show system notification in a non-blocking way"""
        def _notify():
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Dead Link Checker",
                    timeout=5
                )
            except:
                pass
        
        # Always run notifications in a separate thread to avoid blocking GUI
        threading.Thread(target=_notify, daemon=True).start()

    def update_grid(self, result: LinkResult):
        """Update the interactive grid with a new result"""
        self.progress_queue.put(('grid', result))

    def filter_grid(self, event=None):
        """Filter the grid results based on search text"""
        search_query = self.grid_search.get().lower()
        if not self.table:
            return
            
        # Implementation of filtering for CTkTable
        # Since CTkTable doesn't have native filtering, we'll have to redraw or manage data
        # To keep it simple and performant, we'll filter from self.results
        filtered_data = [["URL", "Status", "Type", "Time", "Location"]] # Header
        for r in self.results:
            row = [
                r.url, 
                f"{r.status_code} {r.status_text}", 
                r.link_type, 
                f"{r.response_time}s",
                "External" if r.is_external else "Internal"
            ]
            if any(search_query in str(cell).lower() for cell in row):
                filtered_data.append(row)
        
        self.table.update_values(filtered_data)

    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.pause_button.configure(state="disabled", text="⏸ Pause")
        self.url_entry.configure(state="normal")
        self.progress_bar.set(1)

    def minimize_to_tray(self):
        """Minimize window to system tray"""
        self.withdraw()
        self.show_notification("Dead Link Checker", "App minimized to system tray.")
    
    def log_message(self, message):
        """Add message or LinkResult to status text/grid"""
        if isinstance(message, LinkResult):
            self.progress_queue.put(('grid', message))
        else:
            self.progress_queue.put(('log', message))
    
    def update_statistics(self, results):
        """Update statistics display"""
        if not results:
            return
        
        total = len(results)
        working = len([r for r in results if not r.is_dead])
        broken = len([r for r in results if r.is_dead])
        success_rate = (working / total * 100) if total > 0 else 0
        
        self.progress_queue.put(('stats', {
            'total': total,
            'working': working,
            'broken': broken,
            'success_rate': success_rate
        }))
    
    def monitor_progress(self):
        """Monitor progress queue and update UI in a controlled manner"""
        processed_count = 0
        max_per_tick = 20 # Limit processing to keep UI responsive
        
        try:
            while processed_count < max_per_tick:
                try:
                    msg_type, data = self.progress_queue.get_nowait()
                except queue.Empty:
                    break
                
                processed_count += 1
                
                if msg_type == 'log':
                    self.status_text.configure(state="normal")
                    self.status_text.insert("end", str(data))
                    self.status_text.see("end")
                    self.status_text.configure(state="disabled")
                
                elif msg_type == 'stats':
                    self.total_label.configure(text=str(data['total']))
                    self.working_label.configure(text=str(data['working']))
                    self.broken_label.configure(text=str(data['broken']))
                    self.success_label.configure(text=f"{data['success_rate']:.1f}%")
                
                elif msg_type == 'progress':
                    self.progress_bar.set(data)

                elif msg_type == 'grid':
                    self.results.append(data)
                    self.add_result_to_grid(data)
                    
        except Exception as e:
            print(f"Error in monitor_progress: {e}")
        
        # Schedule next check
        self.after(50, self.monitor_progress)

    def add_result_to_grid(self, result: LinkResult):
        """Add a single result row to the table grid"""
        row_data = [
            result.url, 
            f"{result.status_code if result.status_code else 'Err'} {result.status_text}", 
            result.link_type, 
            f"{result.response_time}s",
            "External" if result.is_external else "Internal"
        ]
        
        if not self.table:
            # Initialize table with headers
            headers = [["URL", "Status", "Type", "Time", "Location"]]
            self.table = CTkTable(
                master=self.grid_table_container, 
                values=headers + [row_data],
                colors=("#2c3e50", "#34495e"),
                header_color="#1a5276",
                hover_color="#34495e",
                anchor="w" # Left align data
            )
            self.table.pack(fill="both", expand=True)
        else:
            self.table.add_row(values=row_data)
        
        # Scroll to bottom
        try:
            self.grid_table_container._parent_canvas.yview_moveto(1.0)
        except:
            pass
    
    def open_reports_folder(self):
        """Open the reports folder"""
        reports_dir = self.config.get("report_dir", "reports")
        
        # If path is relative, make it absolute relative to script location
        if not os.path.isabs(reports_dir):
            reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), reports_dir)
            
        if os.path.exists(reports_dir):
            try:
                open_file(reports_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
        else:
            messagebox.showinfo("Info", f"Reports folder not found at:\n{reports_dir}\n\nPlease generate a report first!")
    
    def clear_results(self):
        """Clear results display"""
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.configure(state="disabled")
        self.progress_bar.set(0)
        self.total_label.configure(text="0")
        self.working_label.configure(text="0")
        self.broken_label.configure(text="0")
        self.success_label.configure(text="0%")
        self.results = []
        self.show_welcome_message()

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("Application Settings")
        self.geometry("550x750")
        self.resizable(True, True)
        self.grab_set()  # Modal
        
        # Center window
        self.center_window()
        
        # UI
        ctk.CTkLabel(self, text="⚙️ GLOBAL SETTINGS", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Report Directory
        ctk.CTkLabel(container, text="Default Report Directory:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.dir_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.dir_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.report_dir_entry = ctk.CTkEntry(self.dir_frame, height=32)
        self.report_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.report_dir_entry.insert(0, self.parent.config.get("report_dir", "reports"))
        
        ctk.CTkButton(self.dir_frame, text="Browse", width=60, height=32, command=self.browse_dir).pack(side="left")
        
        # Default Workers
        ctk.CTkLabel(container, text="Default Worker Size:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.workers_slider = ctk.CTkSlider(container, from_=5, to=50, number_of_steps=9)
        self.workers_slider.pack(fill="x", padx=10, pady=5)
        self.workers_slider.set(self.parent.config.get("workers", 10))
        
        # Default Depth
        ctk.CTkLabel(container, text="Default Crawl Depth:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.depth_slider = ctk.CTkSlider(container, from_=1, to=5, number_of_steps=4)
        self.depth_slider.pack(fill="x", padx=10, pady=5)
        self.depth_slider.set(self.parent.config.get("depth", 1))

        # Check External Default
        self.check_ext_default = ctk.CTkCheckBox(container, text="Check External Links by Default")
        self.check_ext_default.pack(fill="x", padx=10, pady=5)
        if self.parent.config.get("check_external", True): self.check_ext_default.select()
        
        # Default Formats
        ctk.CTkLabel(container, text="Default Report Formats:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        
        format_frame = ctk.CTkFrame(container, fg_color="transparent")
        format_frame.pack(fill="x", padx=10)
        
        self.gen_txt = ctk.CTkCheckBox(format_frame, text="Text (.txt)")
        self.gen_txt.pack(side="left", padx=(10, 20), pady=2)
        if self.parent.config.get("generate_txt", True): self.gen_txt.select()
        
        self.gen_pdf = ctk.CTkCheckBox(format_frame, text="PDF (.pdf)")
        self.gen_pdf.pack(side="left", padx=20, pady=2)
        if self.parent.config.get("generate_pdf", True): self.gen_pdf.select()
        
        self.gen_csv = ctk.CTkCheckBox(format_frame, text="CSV (.csv)")
        self.gen_csv.pack(side="left", padx=20, pady=2)
        if self.parent.config.get("generate_csv", True): self.gen_csv.select()

        # Divider
        ctk.CTkFrame(container, height=2, fg_color="gray30").pack(fill="x", padx=10, pady=15)

        # Browsing Identity (User-Agent)
        ctk.CTkLabel(container, text="Browsing Identity (User-Agent):", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0), padx=10, anchor="w")
        self.ua_var = ctk.StringVar(value=self.parent.config.get("user_agent", "Default"))
        self.ua_menu = ctk.CTkOptionMenu(
            container, 
            values=["Default", "Googlebot", "iPhone (iOS 15)", "Android (Chrome)"],
            variable=self.ua_var
        )
        self.ua_menu.pack(fill="x", padx=10, pady=5)

        # Authentication Section
        ctk.CTkLabel(container, text="Authentication Settings:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        
        self.auth_type_var = ctk.StringVar(value=self.parent.config.get("auth_type", "None"))
        auth_frame = ctk.CTkFrame(container, fg_color="transparent")
        auth_frame.pack(fill="x", padx=10)
        
        ctk.CTkRadioButton(auth_frame, text="None", variable=self.auth_type_var, value="None", command=self.toggle_auth_fields).pack(side="left", padx=(10, 20))
        ctk.CTkRadioButton(auth_frame, text="Basic Auth", variable=self.auth_type_var, value="Basic", command=self.toggle_auth_fields).pack(side="left", padx=20)

        self.auth_fields_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.auth_fields_frame.pack(fill="x", padx=10, pady=5)
        
        self.user_entry = ctk.CTkEntry(self.auth_fields_frame, placeholder_text="Username", height=32)
        self.user_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.user_entry.insert(0, self.parent.config.get("username", ""))
        
        self.pass_entry = ctk.CTkEntry(self.auth_fields_frame, placeholder_text="Password", show="*", height=32)
        self.pass_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.pass_entry.insert(0, self.parent.config.get("password", ""))

        # Cookies Section
        ctk.CTkLabel(container, text="Session Cookies (Raw string):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.cookies_entry = ctk.CTkEntry(container, placeholder_text="name=value; session_id=abc...", height=32)
        self.cookies_entry.pack(fill="x", padx=10, pady=5)
        self.cookies_entry.insert(0, self.parent.config.get("cookies", ""))
        
        # Exclusion Rules Section
        ctk.CTkLabel(container, text="Exclusion Rules (One pattern per line):", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.exclude_rules_text = ctk.CTkTextbox(container, height=100)
        self.exclude_rules_text.pack(fill="x", padx=10, pady=5)
        self.exclude_rules_text.insert("1.0", self.parent.config.get("exclude_rules", ""))
        
        self.toggle_auth_fields()

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(button_frame, text="Save Settings", fg_color="#27ae60", hover_color="#2ecc71", command=self.save).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Cancel", fg_color="#95a5a6", hover_color="#7f8c8d", command=self.destroy).pack(side="left", fill="x", expand=True, padx=(5, 0))

    def browse_dir(self):
        current_dir = self.report_dir_entry.get()
        new_dir = filedialog.askdirectory(initialdir=current_dir)
        if new_dir:
            self.report_dir_entry.delete(0, "end")
            self.report_dir_entry.insert(0, new_dir)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def toggle_auth_fields(self):
        if self.auth_type_var.get() == "Basic":
            self.user_entry.configure(state="normal")
            self.pass_entry.configure(state="normal")
        else:
            self.user_entry.configure(state="disabled")
            self.pass_entry.configure(state="disabled")

    def save(self):
        new_config = {
            "workers": int(self.workers_slider.get()),
            "depth": int(self.depth_slider.get()),
            "timeout": self.parent.config.get("timeout", 10),
            "report_dir": self.report_dir_entry.get(),
            "generate_txt": self.gen_txt.get() == 1,
            "generate_pdf": self.gen_pdf.get() == 1,
            "generate_csv": self.gen_csv.get() == 1,
            "user_agent": self.ua_var.get(),
            "auth_type": self.auth_type_var.get(),
            "username": self.user_entry.get(),
            "password": self.pass_entry.get(),
            "cookies": self.cookies_entry.get(),
            "check_external": self.check_ext_default.get()
        }
        
        self.parent.config = new_config
        save_config(new_config)
        
        # Update parent UI
        self.parent.workers_slider.set(new_config["workers"])
        self.parent.update_workers_label(new_config["workers"])
        self.parent.depth_slider.set(new_config["depth"])
        self.parent.update_depth_label(new_config["depth"])
        
        if new_config["check_external"]: self.parent.check_external.select()
        else: self.parent.check_external.deselect()
        
        if new_config["generate_txt"]: self.parent.generate_txt.select()
        else: self.parent.generate_txt.deselect()
        
        if new_config["generate_pdf"]: self.parent.generate_pdf.select()
        else: self.parent.generate_pdf.deselect()
        
        if new_config["generate_csv"]: self.parent.generate_csv.select()
        else: self.parent.generate_csv.deselect()
        
        # Save exclusion rules to parent
        self.parent.config["exclude_rules"] = self.exclude_rules_text.get("1.0", "end-1c")
        save_config(self.parent.config)
        
        messagebox.showinfo("Success", "Settings saved successfully!")
        self.destroy()

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Report History")
        self.geometry("750x650")
        self.minsize(600, 500)
        self.grab_set()
        self.center_window()

        # UI
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(top_frame, text="📜 REPORT HISTORY", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        
        # Search Box
        search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        search_frame.pack(side="right", fill="y")
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search url or date...", width=250)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.load_history())
        
        ctk.CTkButton(search_frame, text="🔍 Search", width=80, command=self.load_history).pack(side="left")

        # Container for the list
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Recent Analysis Sessions")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.load_history()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def load_history(self):
        """Load history sessions asynchronously to avoid blocking UI"""
        # Clear current list
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip()
        
        # Loading indicator
        ctk.CTkLabel(self.scroll_frame, text="Loading history...", name="loading_label").pack(pady=20)
        
        def fetch_task():
            try:
                sessions = self.parent.db.get_sessions(search_query)
                self.after(0, lambda: self.render_sessions(sessions))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Database Error", str(e)))

        threading.Thread(target=fetch_task, daemon=True).start()

    def render_sessions(self, sessions):
        """Render session cards progressively"""
        # Remove loading label
        for widget in self.scroll_frame.winfo_children():
            if getattr(widget, "_name", "") == "loading_label":
                widget.destroy()

        if not sessions:
            ctk.CTkLabel(self.scroll_frame, text="No matches found in history.", font=ctk.CTkFont(slant="italic")).pack(pady=20)
            return

        # Process in chunks to keep UI responsive
        def render_chunk(remaining_sessions):
            if not remaining_sessions or not self.winfo_exists():
                return
            
            chunk_size = 5
            chunk = remaining_sessions[:chunk_size]
            rest = remaining_sessions[chunk_size:]
            
            for session in chunk:
                self.add_session_card(session)
            
            if rest:
                self.after(10, lambda: render_chunk(rest))

        render_chunk(sessions)

    def add_session_card(self, session):
        reports_dir = self.parent.config.get("report_dir", "reports")
        if not os.path.isabs(reports_dir):
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), reports_dir)
            
        session_folder = session['session_folder']
        session_path = os.path.join(reports_dir, session_folder)
        
        # Display Info
        timestamp = session['timestamp'] # SQLite DATETIME
        url = session['url']
        mode = session['mode']
        total = session['total_links']
        broken = session['broken_links']
        working = session['working_links']

        card = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        card.pack(fill="x", pady=10, padx=5)
        
        header = ctk.CTkFrame(card, fg_color=("#dfe6e9", "#2d3436"), height=40, corner_radius=10)
        header.pack(fill="x")
        
        title_lbl = ctk.CTkLabel(header, text=f"{timestamp} | {url}", font=ctk.CTkFont(size=13, weight="bold"))
        title_lbl.pack(side="left", padx=15, pady=8)
        
        if os.path.exists(session_path):
            open_btn = ctk.CTkButton(header, text="📂 Open Folder", width=100, height=28, 
                                    fg_color="#34495e", hover_color="#2c3e50",
                                    command=lambda p=session_path: open_file(p))
            open_btn.pack(side="right", padx=15, pady=6)
        
        # Stats info
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=5)
        
        stats_text = f"Mode: {mode.capitalize()} | Total: {total} | ✅ Working: {working} | ❌ Broken: {broken}"
        ctk.CTkLabel(stats_frame, text=stats_text, font=ctk.CTkFont(size=11, slant="italic")).pack(side="left")

        # Files list if exists
        if os.path.exists(session_path):
            try:
                files = [f for f in os.listdir(session_path) if os.path.isfile(os.path.join(session_path, f))]
                for filename in files:
                    file_path = os.path.join(session_path, filename)
                    f_frame = ctk.CTkFrame(card, fg_color="transparent")
                    f_frame.pack(fill="x", padx=25, pady=2)
                    
                    icon = "📄"
                    if filename.lower().endswith(".pdf"): icon = "📕"
                    elif filename.lower().endswith(".csv"): icon = "📊"
                    
                    ctk.CTkLabel(f_frame, text=f"{icon} {filename}", font=ctk.CTkFont(size=12)).pack(side="left")
                    
                    f_btn = ctk.CTkButton(f_frame, text="View Report", width=80, height=22, 
                                         font=ctk.CTkFont(size=11),
                                         command=lambda p=file_path: open_file(p))
                    f_btn.pack(side="right")
            except:
                pass
        else:
             ctk.CTkLabel(card, text="⚠️ Folder no longer exists", font=ctk.CTkFont(size=11, slant="italic"), text_color="orange").pack(pady=5)


def main():
    """Main entry point"""
    setup_windows_encoding()
    app = DeadLinkCheckerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
