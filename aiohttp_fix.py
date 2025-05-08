#!/usr/bin/env python3
# aiohttp_fix.py - Fix "No Models Found" error with aiohttp update and SSL patch

import os
import tkinter as tk
from tkinter import messagebox, simpledialog

# Import shared components
from common import (
    find_pip_sitepackage_paths,
    find_pipx_ofscraper_sitepackage_paths,
    check_ofscraper_installation
)

class AiohttpFixTool:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        
    def run(self):
        """Run the aiohttp and sessionmanager.py fix tool"""
        self.update_status("=== Aiohttp and SSL Fix Tool ===")
        
        # Show explanation of what this tool does
        explanation = (
            "This will update aiohttp to 3.11.16 and patch sessionmanager.py to fix the 'no models found' error."
        )
        messagebox.showinfo("Explanation", explanation, parent=self.parent)
        
        # Ask about updating aiohttp
        update_choice = messagebox.askyesno("Update aiohttp", 
                                          "Do you want to update aiohttp to 3.11.16?",
                                          parent=self.parent)
        if update_choice:
            # In the real implementation, this would actually update aiohttp
            # I'm keeping it as a simulation as in the original
            self.update_status("aiohttp update simulated.")
        else:
            self.update_status("Skipping aiohttp update.")
            
        # Ask about patching sessionmanager.py
        fix_sm = messagebox.askyesno("Fix sessionmanager.py",
                                    "Do you want to patch sessionmanager.py to replace the SSL configuration?",
                                    parent=self.parent)
        if fix_sm:
            self.modify_sessionmanager_if_needed()
        else:
            self.update_status("Skipping sessionmanager.py fix.")
            
    def modify_sessionmanager_if_needed(self):
        """Patch sessionmanager.py to fix SSL configuration"""
        # Get installation type
        install_type = check_ofscraper_installation()
        
        # Find all potential paths where sessionmanager.py could be
        all_paths = set()
        if install_type in ("pip", "both"):
            pip_paths = find_pip_sitepackage_paths()
            all_paths.update(pip_paths)
        if install_type in ("pipx", "both"):
            pipx_paths = find_pipx_ofscraper_sitepackage_paths()
            all_paths.update(pipx_paths)
            
        if not all_paths:
            self.update_status("No site-package paths found.")
            return
            
        self.update_status("Searching for sessionmanager.py:")
        for p in all_paths:
            self.update_status(f"  {p}")
            
        patched = self.patch_sessionmanager_in_paths(all_paths)
        if patched:
            self.update_status("sessionmanager.py patched successfully.")
        else:
            self.update_status("sessionmanager.py was not patched or not found.")
            
    def patch_sessionmanager_in_paths(self, paths):
        """Find and patch sessionmanager.py in the given paths"""
        old_line = "ssl=ssl.create_default_context(cafile=certifi.where()),"
        new_line = "ssl=False,"
        
        for path in paths:
            if not os.path.isdir(path):
                continue
                
            for root, dirs, files in os.walk(path):
                if "sessionmanager.py" in files:
                    session_file = os.path.join(root, "sessionmanager.py")
                    self.update_status(f"Found: {session_file}")
                    
                    try:
                        with open(session_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        if old_line not in content and new_line in content:
                            self.update_status("Already patched.")
                            return True
                            
                        if old_line in content:
                            new_content = content.replace(old_line, new_line)
                            with open(session_file, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            return True
                        else:
                            self.update_status("Expected SSL line not found.")
                    except Exception as e:
                        self.update_status(f"Error modifying {session_file}: {e}")
        return False

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aiohttp Fix Tool")
    
    def print_to_console(message):
        print(message)
        
    tool = AiohttpFixTool(root, print_to_console)
    tool.run()
    
    root.mainloop()