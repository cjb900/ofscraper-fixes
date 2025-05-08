#!/usr/bin/env python3
# aiolimiter_fix.py - Fix "Finished Script" error with aiolimiter

import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

# Import shared components
from common import (
    RECOMMENDED_AIOLIMITER,
    check_ofscraper_installation
)

class AiolimiterFixTool:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        
    def run(self):
        """Run the aiolimiter fix tool"""
        self.update_status("=== Aiolimiter Fix Tool ===")
        
        # Check if user wants to proceed
        fix_dialog = messagebox.askyesno("Fix aiolimiter",
                                       "This will set aiolimiter to 1.1.0 to fix ofscraper ending with 'Finish Script'.\nDo you want to fix aiolimiter?",
                                       parent=self.parent)
        if not fix_dialog:
            self.update_status("Skipping aiolimiter fix.")
            return
            
        # Detect installation type
        install_type = check_ofscraper_installation()
        if install_type is None:
            self.update_status("ofscraper not found. Installing aiolimiter via pip may not be effective.")
            if messagebox.askyesno("Install aiolimiter", 
                                 "Install aiolimiter via pip?",
                                 parent=self.parent):
                self.install_aiolimiter_via_pip()
            return
            
        # Apply the fix based on installation type
        self.update_status("Installing aiolimiter==1.1.0...")
        if install_type in ["pip", "both"]:
            self.install_aiolimiter_via_pip()
        elif install_type == "pipx":
            self.install_aiolimiter_via_pipx()
        
    def install_aiolimiter_via_pip(self):
        """Install aiolimiter via pip"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade",
                          RECOMMENDED_AIOLIMITER, "--force-reinstall"],
                          check=True, text=True)
            self.update_status("aiolimiter installed successfully via pip.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"Error installing aiolimiter via pip:\n{e}")
            
    def install_aiolimiter_via_pipx(self):
        """Install aiolimiter via pipx inject"""
        try:
            subprocess.run(["pipx", "inject", "ofscraper", RECOMMENDED_AIOLIMITER, "--force"],
                          check=True, text=True)
            self.update_status("aiolimiter injected successfully via pipx.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"Error injecting aiolimiter via pipx:\n{e}")

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aiolimiter Fix Tool")
    
    def print_to_console(message):
        print(message)
        
    tool = AiolimiterFixTool(root, print_to_console)
    tool.run()
    
    root.mainloop()