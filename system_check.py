#!/usr/bin/env python3
# system_check.py - Check system compatibility for ofScraper

import sys
import subprocess
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog

# Import shared components
from common import (
    RECOMMENDED_OS_VERSION, 
    RECOMMENDED_PYTHON_VERSION, 
    PYTHON_DOWNLOAD_URL,
    check_ofscraper_installation,
    get_ofscraper_version
)

class SystemCheckTool:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.install_type = None
        
    def run(self):
        """Run the system check tool"""
        # Report Python version and interpreter path
        self.update_status(f"Script is running with: {sys.executable}")
        ver = sys.version_info
        current_py = f"{ver.major}.{ver.minor}.{ver.micro}"
        self.update_status(f"You are currently using Python {current_py}")
        
        # Check Python version compatibility
        if ver.major != 3 or ver.minor < 11 or ver.minor >= 13:
            warn_text = (f"You are currently using Python {current_py}.\n"
                        "This version will not work with ofscraper.\n"
                        f"For best compatibility, please install Python {RECOMMENDED_PYTHON_VERSION}.")
            if messagebox.askyesno("Python Version Warning", warn_text + "\nWould you like to open the download page?", 
                                  parent=self.parent):
                webbrowser.open(PYTHON_DOWNLOAD_URL)
            return
            
        if current_py != RECOMMENDED_PYTHON_VERSION:
            self.update_status("Note: The recommended Python version is 3.11.6. If you have Python issues, please install Python 3.11.6.")
            
        self.update_status("=== Combined System Check & Update ===")
        
        # Check ofscraper installation
        self.install_type = check_ofscraper_installation()
        if self.install_type is None:
            self.update_status("ofscraper is NOT detected via pip or pipx.")
        elif self.install_type == "both":
            self.update_status("ofscraper is installed with BOTH pip and pipx.")
        elif self.install_type == "pip":
            self.update_status("ofscraper is installed via pip.")
        elif self.install_type == "pipx":
            self.update_status("ofscraper is installed via pipx.")
            
        # Check ofscraper version
        version = get_ofscraper_version(self.install_type)
        self.update_status(f"Detected ofscraper version: {version}")
        
        if self.install_type is None:
            self.update_status("Warning: ofscraper is not detected via pip or pipx.\nPlease reinstall via pip or pipx to get version " + RECOMMENDED_OS_VERSION + ".")
            return
            
        if version == "unknown":
            self.update_status("Could not determine ofscraper version.")
            return
            
        # Compare versions
        try:
            current_version = tuple(map(int, version.split(".")))
            recommended_version = tuple(map(int, RECOMMENDED_OS_VERSION.split(".")))
        except Exception as e:
            self.update_status(f"Error parsing version numbers: {e}")
            return
            
        # Offer update if needed
        if current_version < recommended_version:
            self.update_status(f"ofscraper is not at the recommended version ({RECOMMENDED_OS_VERSION}).")
            if messagebox.askyesno("Update ofscraper", 
                                  f"Your ofscraper version is {version}.\nWould you like to update to version {RECOMMENDED_OS_VERSION}?",
                                  parent=self.parent):
                self.update_ofscraper()
            else:
                self.update_status("Update ofscraper not performed.")
        else:
            self.update_status("ofscraper is up-to-date!")
        
        return self.install_type
        
    def update_ofscraper(self):
        """Update ofscraper to the recommended version"""
        if self.install_type == "pip":
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", 
                               f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                               check=True, text=True)
                self.update_status("ofscraper updated successfully via pip.")
            except subprocess.CalledProcessError as e:
                self.update_status(f"Error updating via pip:\n{e}")
                
        elif self.install_type == "pipx":
            try:
                subprocess.run(["pipx", "upgrade", "ofscraper"], 
                               check=True, text=True)
                self.update_status("ofscraper updated successfully via pipx.")
            except subprocess.CalledProcessError as e:
                self.update_status(f"Error updating via pipx:\n{e}")
                
        elif self.install_type == "both":
            method = simpledialog.askinteger("Update ofscraper",
                                           "Select update method:\n1) pip\n2) pipx\n3) Both",
                                           minvalue=1, maxvalue=3, parent=self.parent)
            if method == 1:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", 
                                   f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                                   check=True, text=True)
                    self.update_status("ofscraper updated successfully via pip.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error updating via pip:\n{e}")
                    
            elif method == 2:
                try:
                    subprocess.run(["pipx", "upgrade", "ofscraper"], 
                                   check=True, text=True)
                    self.update_status("ofscraper updated successfully via pipx.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error updating via pipx:\n{e}")
                    
            elif method == 3:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", 
                                   f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                                   check=True, text=True)
                    subprocess.run(["pipx", "upgrade", "ofscraper"], 
                                   check=True, text=True)
                    self.update_status("ofscraper updated successfully via both pip and pipx.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error updating via both methods:\n{e}")
                    
        # Verify the updated version
        new_version = get_ofscraper_version(self.install_type)
        self.update_status(f"Updated ofscraper version: {new_version}")

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("System Check")
    
    def print_to_console(message):
        print(message)
        
    checker = SystemCheckTool(root, print_to_console)
    checker.run()
    
    root.mainloop()