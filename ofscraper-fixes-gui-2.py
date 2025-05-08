#!/usr/bin/env python3
# ofscraper_fixes_gui.py - Main GUI for ofScraper fix tools

import tkinter as tk
from tkinter import ttk, messagebox

# Import modules for each tool
from common import ASCII_LOGO
from system_check import SystemCheckTool
from aiolimiter_fix import AiolimiterFixTool
from aiohttp_fix import AiohttpFixTool
from config_fix import ConfigFixTool
from test_run import TestRunTool
from reinstall import ReinstallTool

class SetupOfScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup ofScraper")
        self.root.geometry("645x675")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Display the ASCII logo
        logo_label = tk.Label(self.main_frame, text=ASCII_LOGO, font=("Courier", 10), justify=tk.LEFT)
        logo_label.grid(row=0, column=0, columnspan=2, pady=(5, 10))
        
        # Store installation type discovered during system check
        self.install_type = None
        
        # Create the GUI components
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets in the main GUI"""
        # Instructions label
        instructions_label = ttk.Label(
            self.main_frame,
            text="Click the buttons below to perform setup tasks:",
            font=("TkDefaultFont", 10, "bold")
        )
        instructions_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Row 0 in button_frame - Start Here button
        start_here_button = ttk.Button(
            button_frame,
            text="Start Here",
            command=self.run_system_check
        )
        start_here_button.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        # Row 1 in button_frame - Two column buttons
        finished_script_button = ttk.Button(
            button_frame,
            text="Finished Script Fix",
            command=self.run_aiolimiter_fix
        )
        finished_script_button.grid(row=1, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        update_aiohttp_button = ttk.Button(
            button_frame,
            text="No Model Found Fix",
            command=self.run_aiohttp_fix
        )
        update_aiohttp_button.grid(row=1, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        # Row 2 in button_frame - Two column buttons
        auth_config_button = ttk.Button(
            button_frame,
            text="Auth/Config Fix & DRM Info",
            command=self.run_config_fix
        )
        auth_config_button.grid(row=2, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        test_run_button = ttk.Button(
            button_frame,
            text="Test Run ofscraper",
            command=self.run_test_tool
        )
        test_run_button.grid(row=2, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        # Row 3 in button_frame - Reinstall button
        reinstall_button = ttk.Button(
            button_frame,
            text="Reinstall ofscraper",
            command=self.run_reinstall_tool
        )
        reinstall_button.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        # Log area
        log_label = ttk.Label(
            self.main_frame,
            text="Log of actions:",
            font=("TkDefaultFont", 10, "bold")
        )
        log_label.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.log_area = tk.Text(self.main_frame, wrap=tk.WORD, height=10, width=70)
        self.log_area.insert(tk.END, "Actions and status will appear here...\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Add scrollbar to log area
        log_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.log_area.yview)
        log_scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.log_area.config(yscrollcommand=log_scrollbar.set)
        
        # Configure column and row weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
    def update_status(self, message):
        """Update the log area with a new message"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)
        
    def run_system_check(self):
        """Run the system check tool"""
        try:
            tool = SystemCheckTool(self.root, self.update_status)
            self.install_type = tool.run()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during system check: {e}", parent=self.root)
            self.update_status(f"Error: {e}")
            
    def run_aiolimiter_fix(self):
        """Run the aiolimiter fix tool"""
        try:
            tool = AiolimiterFixTool(self.root, self.update_status)
            tool.run()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during aiolimiter fix: {e}", parent=self.root)
            self.update_status(f"Error: {e}")
            
    def run_aiohttp_fix(self):
        """Run the aiohttp and sessionmanager.py fix tool"""
        try:
            tool = AiohttpFixTool(self.root, self.update_status)
            tool.run()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during aiohttp fix: {e}", parent=self.root)
            self.update_status(f"Error: {e}")
            
    def run_config_fix(self):
        """Run the config.json fix tool"""
        try:
            tool = ConfigFixTool(self.root, self.update_status)
            tool.run()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during config fix: {e}", parent=self.root)
            self.update_status(f"Error: {e}")
            
    def run_test_tool(self):
        """Run the test tool"""
        try:
            tool = TestRunTool(self.root, self.update_status)
            # Pass the installation type discovered during system check
            tool.run()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during test run: {e}", parent=self.root)
            self.update_status(f"Error: {e}")
            
    def run_reinstall_tool(self):
        """Run the reinstall tool"""
        try:
            tool = ReinstallTool(self.root, self.update_status)
            tool.run()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during reinstall: {e}", parent=self.root)
            self.update_status(f"Error: {e}")

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = SetupOfScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()