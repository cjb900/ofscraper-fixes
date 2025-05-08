#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess

# Import common functions
from common import (
    check_ofscraper_installation,
    find_pip_sitepackage_paths,
    find_pipx_ofscraper_sitepackage_paths
)

class ModelsFixWindow:
    def __init__(self, parent):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title("No Models Found Fix")
        self.top.geometry("550x400")
        
        # Create UI elements
        self.create_widgets()
        
        # Detect installation and prepare for fix
        self.detect_installation()
        
    def create_widgets(self):
        # Frame for output
        main_frame = tk.Frame(self.top, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Explanation label
        explanation = (
            "This will update aiohttp to 3.11.16 and patch sessionmanager.py to fix "
            "the 'No Models Found' error. The patch disables SSL verification for connections."
        )
        label = tk.Label(main_frame, text=explanation, wraplength=500, justify=tk.LEFT)
        label.pack(anchor=tk.W, pady=10)
        
        # Log area
        self.log_area = tk.Text(main_frame, wrap=tk.WORD, height=15, width=65)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar = tk.Scrollbar(main_frame, command=self.log_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_area.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(main_frame, pady=10)
        button_frame.pack(fill=tk.X)
        
        update_aiohttp_button = tk.Button(button_frame, text="Update aiohttp", 
                                        command=self.update_aiohttp)
        update_aiohttp_button.pack(side=tk.LEFT, padx=5)
        
        patch_button = tk.Button(button_frame, text="Patch SessionManager", 
                               command=self.patch_sessionmanager)
        patch_button.pack(side=tk.LEFT, padx=5)
        
        close_button = tk.Button(button_frame, text="Close", command=self.top.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
    
    def update_status(self, message):
        """Update the log area with a message."""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.top.update()
    
    def detect_installation(self):
        """Detect ofScraper installation type and prepare paths."""
        self.update_status("Detecting ofScraper installation...")
        self.install_type = check_ofscraper_installation()
        
        if self.install_type is None:
            self.update_status("ofScraper is not detected via pip or pipx.")
            self.update_status("Fixes may not be effective.")
            return
        
        if self.install_type == "pip":
            self.update_status("ofScraper is installed via pip.")
        elif self.install_type == "pipx":
            self.update_status("ofScraper is installed via pipx.")
        elif self.install_type == "both":
            self.update_status("ofScraper is installed with BOTH pip and pipx.")
        
        # Find potential site-package paths
        self.all_paths = set()
        if self.install_type in ("pip", "both"):
            pip_paths = find_pip_sitepackage_paths()
            self.all_paths.update(pip_paths)
            self.update_status(f"Found {len(pip_paths)} pip site-package paths.")
        
        if self.install_type in ("pipx", "both"):
            pipx_paths = find_pipx_ofscraper_sitepackage_paths()
            self.all_paths.update(pipx_paths)
            self.update_status(f"Found {len(pipx_paths)} pipx site-package paths.")
        
        if not self.all_paths:
            self.update_status("No site-package paths found.")
        else:
            self.update_status("Ready to apply fixes. Use the buttons below.")
    
    def update_aiohttp(self):
        """Update aiohttp package."""
        if self.install_type is None:
            self.update_status("ofScraper installation not detected. Update may not be effective.")
        
        self.update_status("Updating aiohttp to 3.11.16...")
        
        if self.install_type in ["pip", "both"]:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", 
                              "aiohttp==3.11.16"],
                             check=True, text=True)
                self.update_status("aioself.update_status("aiohttp updated successfully via pip.")
            except subprocess.CalledProcessError as e:
                self.update_status(f"Error updating aiohttp via pip:\n{e}")
        
        if self.install_type in ["pipx", "both"]:
            try:
                subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.16", "--force"],
                             check=True, text=True)
                self.update_status("aiohttp updated successfully via pipx.")
            except subprocess.CalledProcessError as e:
                self.update_status(f"Error updating aiohttp via pipx:\n{e}")
    
    def patch_sessionmanager(self):
        """Patch sessionmanager.py to fix SSL configuration."""
        if not self.all_paths:
            self.update_status("No site-package paths found. Cannot patch sessionmanager.py.")
            return
        
        self.update_status("Searching for sessionmanager.py in site-packages...")
        
        old_line = "ssl=ssl.create_default_context(cafile=certifi.where()),"
        new_line = "ssl=False,"
        
        patched = False
        for path in self.all_paths:
            if not os.path.isdir(path):
                continue
            
            self.update_status(f"Searching in: {path}")
            
            for root, dirs, files in os.walk(path):
                if "sessionmanager.py" in files:
                    session_file = os.path.join(root, "sessionmanager.py")
                    self.update_status(f"Found: {session_file}")
                    
                    try:
                        with open(session_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        if old_line not in content and new_line in content:
                            self.update_status("File is already patched.")
                            patched = True
                            continue
                        
                        if old_line in content:
                            new_content = content.replace(old_line, new_line)
                            with open(session_file, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            self.update_status("Successfully patched sessionmanager.py")
                            patched = True
                        else:
                            self.update_status("Expected SSL line not found in this file.")
                    except Exception as e:
                        self.update_status(f"Error modifying {session_file}: {e}")
        
        if not patched:
            self.update_status("Could not find or patch sessionmanager.py.")
        else:
            self.update_status("Patch completed. You can now close this window.")

def run(parent):
    """Create and show the models fix window."""
    return ModelsFixWindow(parent)