#!/usr/bin/env python3
# reinstall.py - Uninstall and reinstall ofScraper

import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

# Import shared components
from common import (
    RECOMMENDED_OS_VERSION,
    check_ofscraper_installation
)

class ReinstallTool:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.install_type = None
        
    def run(self):
        """Run the reinstall tool"""
        self.update_status("=== Reinstall ofScraper Tool ===")
        
        # Check current installation type
        self.install_type = check_ofscraper_installation()
        
        if self.install_type is None:
            self.update_status("No existing ofScraper installation detected.")
            # Skip uninstall, go directly to install
            self.offer_install()
            return
            
        # Ask if user wants to uninstall first
        if not messagebox.askyesno("Reinstall ofScraper", 
                                 "Do you want to uninstall ofScraper first?", 
                                 parent=self.parent):
            self.update_status("Uninstallation skipped.")
        else:
            self.uninstall_ofscraper()
            
        # Ask if user wants to reinstall
        self.offer_install()
        
    def uninstall_ofscraper(self):
        """Uninstall ofScraper based on installation type"""
        if self.install_type == "pip":
            try:
                subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "ofscraper"],
                              check=True, text=True)
                self.update_status("ofScraper uninstalled successfully via pip.")
            except subprocess.CalledProcessError as e:
                self.update_status(f"Error uninstalling via pip:\n{e}")
                
        elif self.install_type == "pipx":
            try:
                subprocess.run(["pipx", "uninstall", "ofscraper"],
                              check=True, text=True)
                self.update_status("ofScraper uninstalled successfully via pipx.")
            except subprocess.CalledProcessError as e:
                self.update_status(f"Error uninstalling via pipx:\n{e}")
                
        elif self.install_type == "both":
            method = simpledialog.askinteger("Uninstall ofScraper",
                                           "Select uninstall method:\n1) pip\n2) pipx\n3) Both",
                                           minvalue=1, maxvalue=3, parent=self.parent)
            if method == 1:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "ofscraper"],
                                  check=True, text=True)
                    self.update_status("ofScraper uninstalled successfully via pip.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error uninstalling via pip:\n{e}")
                    
            elif method == 2:
                try:
                    subprocess.run(["pipx", "uninstall", "ofscraper"],
                                  check=True, text=True)
                    self.update_status("ofScraper uninstalled successfully via pipx.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error uninstalling via pipx:\n{e}")
                    
            elif method == 3:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "ofscraper"],
                                  check=True, text=True)
                    subprocess.run(["pipx", "uninstall", "ofscraper"],
                                  check=True, text=True)
                    self.update_status("ofScraper uninstalled successfully via both pip and pipx.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error uninstalling via both methods:\n{e}")
        
    def offer_install(self):
        """Ask if user wants to reinstall and handle installation"""
        if messagebox.askyesno("Reinstall ofScraper", 
                             "Do you want to reinstall ofScraper?", 
                             parent=self.parent):
            # Ask which method to use for install
            method = simpledialog.askinteger("Install ofScraper",
                                           "Select install method:\n1) pip\n2) pipx",
                                           minvalue=1, maxvalue=2, parent=self.parent)
            if method == 1:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                                  check=True, text=True)
                    self.update_status("ofScraper installed successfully via pip.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error installing via pip:\n{e}")
                    
            elif method == 2:
                try:
                    subprocess.run(["pipx", "install", f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                                  check=True, text=True)
                    self.update_status("ofScraper installed successfully via pipx.")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"Error installing via pipx:\n{e}")
            else:
                self.update_status("No valid install option selected.")
        else:
            self.update_status("Reinstallation skipped.")
            
        # Verify installation after reinstall
        new_install_type = check_ofscraper_installation()
        if new_install_type:
            self.update_status(f"ofScraper is now installed via {new_install_type}.")
        else:
            self.update_status("ofScraper is not installed.")

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Reinstall Tool")
    
    def print_to_console(message):
        print(message)
        
    tool = ReinstallTool(root, print_to_console)
    tool.run()
    
    root.mainloop()