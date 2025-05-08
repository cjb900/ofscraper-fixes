#!/usr/bin/env python3
# config_fix.py - Fix config.json and auth settings for ofScraper

import os
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog

# Import shared components
from common import (
    WRITTEN_GUIDE_URL,
    YOUTUBE_VIDEO_URL,
    open_in_text_editor
)

# Update the recommended URL
NEW_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/rafa-9/dynamic-rules/main/rules.json"
OLD_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"

class ConfigFixTool:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        
    def run(self):
        """Run the config.json fix tool"""
        self.update_status("=== Config and Auth Fix Tool ===")
        
        config_path = os.path.expanduser("~/.config/ofscraper/config.json")
        
        # Ask if user wants to proceed
        if not messagebox.askyesno("Auth Config Fix", 
                                 "Check and fix ofscraper's config.json?",
                                 parent=self.parent):
            self.update_status("Skipping config.json modification.")
            return
            
        # Check if config.json exists
        if not os.path.isfile(config_path):
            self.update_status(f"{config_path} not found.")
            if messagebox.askyesno("Create config.json", 
                                 "Create new config.json with recommended settings?",
                                 parent=self.parent):
                try:
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                    default_config = {
                        "advanced_options": {
                            "dynamic-mode-default": "generic",
                            "custom_values": {"DYNAMIC_GENERIC_URL": NEW_DYNAMIC_GENERIC_URL}
                        },
                        "cdm_options": {"key-mode-default": "manual"}
                    }
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(default_config, f, indent=2)
                    self.update_status(f"Created new config.json at {config_path}.")
                    self.check_key_mode_default(default_config)
                except Exception as e:
                    self.update_status(f"Failed to create config.json: {e}")
            else:
                self.update_status("Skipping config creation.")
            return
            
        # Read existing config.json
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            self.update_status(f"Failed to read config.json: {e}")
            return

        # Update configuration values
        if "advanced_options" not in config_data or config_data["advanced_options"] is None:
            config_data["advanced_options"] = {}
        adv_options = config_data["advanced_options"]
        
        if adv_options.get("dynamic-mode-default") != "generic":
            adv_options["dynamic-mode-default"] = "generic"
            self.update_status("Set advanced_options.dynamic-mode-default to 'generic'.")
            
        # Handle custom_values based on specific cases
        if "custom_values" not in adv_options or adv_options["custom_values"] is None:
            adv_options["custom_values"] = {"DYNAMIC_GENERIC_URL": NEW_DYNAMIC_GENERIC_URL}
            self.update_status(f"Set advanced_options.custom_values with new DYNAMIC_GENERIC_URL.")
        else:
            cv = adv_options["custom_values"]
            current_url = cv.get("DYNAMIC_GENERIC_URL")
            
            # Check if URL is the old one that needs updating
            if current_url == OLD_DYNAMIC_GENERIC_URL:
                cv["DYNAMIC_GENERIC_URL"] = NEW_DYNAMIC_GENERIC_URL
                self.update_status(f"Updated DYNAMIC_GENERIC_URL from old to new URL.")
            # If URL is missing or different from desired URL, set it
            elif current_url is None or current_url != NEW_DYNAMIC_GENERIC_URL:
                cv["DYNAMIC_GENERIC_URL"] = NEW_DYNAMIC_GENERIC_URL
                self.update_status(f"Set DYNAMIC_GENERIC_URL to new URL.")

        # Ensure CDM options are set
        if "cdm_options" not in config_data or config_data["cdm_options"] is None:
            config_data["cdm_options"] = {}
        cdm_options = config_data["cdm_options"]
        
        if cdm_options.get("key-mode-default") != "manual":
            cdm_options["key-mode-default"] = "manual"
            self.update_status("Set cdm_options.key-mode-default to 'manual'.")

        # Save updated config.json
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            self.update_status("Config.json updated successfully.")
            self.check_key_mode_default(config_data)
        except Exception as e:
            self.update_status(f"Failed to update config.json: {e}")

        # Offer to open auth.json for editing
        auth_prompt = (
            "If your auth is still failing, clear your browser's cookies and cache.\n"
            "DO NOT USE the browser extension—get your auth manually and enter it into auth.json directly.\n\n"
            "Open auth.json in your default text editor?"
        )
        if messagebox.askyesno("Open auth.json", auth_prompt, parent=self.parent):
            auth_path = os.path.expanduser("~/.config/ofscraper/main_profile/auth.json")
            if not os.path.isfile(auth_path):
                os.makedirs(os.path.dirname(auth_path), exist_ok=True)
                with open(auth_path, "w", encoding="utf-8") as f:
                    f.write("{}")
                self.update_status(f"Created new auth.json at {auth_path}.")
            try:
                open_in_text_editor(auth_path)
            except Exception as e:
                self.update_status(f"Error opening auth.json: {e}")
                
    def check_key_mode_default(self, config_data):
        """Check key-mode-default and offer DRM key information"""
        # Always ensure key-mode-default is set to manual
        cdm_opts = config_data.get("cdm_options", {})
        key_mode = cdm_opts.get("key-mode-default")
        
        if key_mode != "manual":
            self.update_status("Warning: key-mode-default is not set to 'manual'. It has been updated to 'manual'.")
            cdm_opts["key-mode-default"] = "manual"
        else:
            self.update_status("key-mode-default is set to 'manual'.")
            
        # Offer DRM key information
        if messagebox.askyesno("Obtain Manual DRM Keys", 
                             "Would you like information on obtaining manual DRM keys?",
                             parent=self.parent):
            choice = simpledialog.askinteger("DRM Keys Info", 
                                           "Select source:\n1. Written guide\n2. YouTube video (Windows only)",
                                           minvalue=1, maxvalue=2, parent=self.parent)
            if choice == 1:
                webbrowser.open(WRITTEN_GUIDE_URL)
                self.update_status(f"Opened written guide: {WRITTEN_GUIDE_URL}")
            elif choice == 2:
                webbrowser.open(YOUTUBE_VIDEO_URL)
                self.update_status(f"Opened YouTube video (Windows only): {YOUTUBE_VIDEO_URL}")
            else:
                self.update_status("No valid option selected.")
        else:
            self.update_status("Manual DRM keys info not requested.")

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Config Fix Tool")
    
    def print_to_console(message):
        print(message)
        
    tool = ConfigFixTool(root, print_to_console)
    tool.run()
    
    root.mainloop()