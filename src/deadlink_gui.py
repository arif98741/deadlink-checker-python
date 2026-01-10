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

# Import the core functionality from deadlink_checker
from deadlink_checker import (
    check_all_links, 
    generate_report, 
    save_report, 
    generate_pdf_report,
    generate_csv_report,
    get_report_filename,
    LinkResult
)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


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
        
        # Initialize variables
        self.is_checking = False
        self.results = []
        self.current_url = ""
        self.progress_queue = queue.Queue()
        
        # Create UI
        self.create_widgets()
        
        # Start progress monitor
        self.monitor_progress()
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # ==================== HEADER ====================
        header_frame = ctk.CTkFrame(self, fg_color=("#1a5276", "#0d2840"), corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Left side - Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔗 DEAD LINK CHECKER",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#ffffff"
        )
        title_label.grid(row=0, column=0, pady=20, padx=20, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Professional Website Link Analysis & Reporting Tool",
            font=ctk.CTkFont(size=14),
            text_color="#a8d5ff"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="w")
        
        # Right side - Version, Copyright, Owner
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=2, pady=20, padx=20, sticky="e")
        
        version_label = ctk.CTkLabel(
            info_frame,
            text="Version 2.0",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffffff"
        )
        version_label.pack(anchor="e", pady=2)
        
        copyright_label = ctk.CTkLabel(
            info_frame,
            text="© 2026 All Rights Reserved",
            font=ctk.CTkFont(size=11),
            text_color="#a8d5ff"
        )
        copyright_label.pack(anchor="e", pady=2)
        
        owner_label = ctk.CTkLabel(
            info_frame,
            text="arif98741",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff"
        )
        owner_label.pack(anchor="e", pady=2)
        
        # Website link (clickable)
        website_label = ctk.CTkLabel(
            info_frame,
            text="devtobox.com",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#4da6ff",
            cursor="hand2"
        )
        website_label.pack(anchor="e", pady=2)
        website_label.bind("<Button-1>", lambda e: webbrowser.open("https://devtobox.com"))
        
        # ==================== LEFT PANEL - CONTROLS ====================
        left_panel = ctk.CTkFrame(self, corner_radius=10)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=400)
        self.grid_columnconfigure(1, weight=1)
        
        # URL Input Section
        url_label = ctk.CTkLabel(
            left_panel,
            text="Target Website URL",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        url_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.url_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text="https://example.com",
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
        self.depth_slider.set(1)
        
        self.depth_value_label = ctk.CTkLabel(
            depth_frame,
            text="1",
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
        self.workers_slider.set(10)
        
        self.workers_value_label = ctk.CTkLabel(
            workers_frame,
            text="10",
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
        self.timeout_slider.set(10)
        
        self.timeout_value_label = ctk.CTkLabel(
            timeout_frame,
            text="10s",
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
        self.generate_txt.select()
        
        self.generate_pdf = ctk.CTkCheckBox(
            left_panel,
            text="Generate PDF Report (.pdf)",
            font=ctk.CTkFont(size=13)
        )
        self.generate_pdf.pack(pady=5, padx=20, anchor="w")
        self.generate_pdf.select()
        
        self.generate_csv = ctk.CTkCheckBox(
            left_panel,
            text="Generate CSV Report (.csv)",
            font=ctk.CTkFont(size=13)
        )
        self.generate_csv.pack(pady=5, padx=20, anchor="w")
        self.generate_csv.select()
        
        # Action Buttons
        button_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        button_frame.pack(pady=30, padx=20, fill="x")
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start Analysis",
            command=self.start_check,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#27ae60", "#1e8449"),
            hover_color=("#229954", "#196f3d")
        )
        self.start_button.pack(fill="x", pady=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Stop Analysis",
            command=self.stop_check,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#c0392b", "#922b21"),
            hover_color=("#a93226", "#7b241c"),
            state="disabled"
        )
        self.stop_button.pack(fill="x", pady=5)
        
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
        
        # Progress/Status Display
        self.status_text = ctk.CTkTextbox(
            right_panel,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.status_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(right_panel)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.progress_bar.set(0)
        
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
        welcome = """
╔══════════════════════════════════════════════════════════════╗
║           Welcome to Dead Link Checker v2.0                  ║
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
        
        # Update UI state
        self.is_checking = True
        self.current_url = url
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.url_entry.configure(state="disabled")
        
        # Clear previous results
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.configure(state="disabled")
        self.progress_bar.set(0)
        
        # Start checking in a separate thread
        thread = threading.Thread(
            target=self.check_links_thread,
            args=(url, depth, workers, timeout),
            daemon=True
        )
        thread.start()
    
    def check_links_thread(self, url, depth, workers, timeout):
        """Thread function to check links"""
        try:
            self.log_message(f"🚀 Starting analysis of: {url}\n")
            self.log_message(f"⚙️  Settings: Depth={depth}, Workers={workers}, Timeout={timeout}s\n")
            self.log_message("=" * 60 + "\n\n")
            
            # Check links with progress callback
            results = check_all_links(url, workers, timeout, depth, self.log_message)
            
            if not self.is_checking:
                self.log_message("\n⚠️  Analysis stopped by user.\n")
                return
            
            self.results = results
            
            # Generate report
            self.log_message("\n" + "=" * 60 + "\n")
            self.log_message("📊 Generating reports...\n\n")
            
            report = generate_report(results)
            self.log_message(report + "\n")
            
            # Save reports
            if self.generate_txt.get():
                txt_filename = get_report_filename(url, "txt")
                save_report(report, txt_filename)
                self.log_message(f"\n✅ Text report saved: {txt_filename}\n")
            
            if self.generate_pdf.get():
                pdf_filename = get_report_filename(url, "pdf")
                generate_pdf_report(results, pdf_filename, url)
                self.log_message(f"✅ PDF report saved: {pdf_filename}\n")
            
            if self.generate_csv.get():
                csv_filename = get_report_filename(url, "csv")
                generate_csv_report(results, csv_filename, url)
                self.log_message(f"✅ CSV report saved: {csv_filename}\n")
            
            # Update statistics
            self.update_statistics(results)
            
            self.log_message("\n🎉 Analysis complete!\n")
            
        except Exception as e:
            self.log_message(f"\n❌ Error: {str(e)}\n")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.is_checking = False
            self.after(0, self.reset_ui)
    
    def stop_check(self):
        """Stop the checking process"""
        self.is_checking = False
        self.log_message("\n⏹ Stopping analysis...\n")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.url_entry.configure(state="normal")
        self.progress_bar.set(1)
    
    def log_message(self, message):
        """Add message to status text"""
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
        """Monitor progress queue and update UI"""
        try:
            while True:
                msg_type, data = self.progress_queue.get_nowait()
                
                if msg_type == 'log':
                    self.status_text.configure(state="normal")
                    self.status_text.insert("end", data)
                    self.status_text.see("end")
                    self.status_text.configure(state="disabled")
                
                elif msg_type == 'stats':
                    self.total_label.configure(text=str(data['total']))
                    self.working_label.configure(text=str(data['working']))
                    self.broken_label.configure(text=str(data['broken']))
                    self.success_label.configure(text=f"{data['success_rate']:.1f}%")
                
                elif msg_type == 'progress':
                    self.progress_bar.set(data)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(100, self.monitor_progress)
    
    def open_reports_folder(self):
        """Open the reports folder"""
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        if os.path.exists(reports_dir):
            os.startfile(reports_dir)
        else:
            messagebox.showinfo("Info", "No reports folder found. Generate a report first!")
    
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


def main():
    """Main entry point"""
    app = DeadLinkCheckerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
