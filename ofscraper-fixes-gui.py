#!/usr/bin/env python3

import sys
import subprocess
import site
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# Use Pillow for robust image loading (supports more PNG formats)
from PIL import Image, ImageTk

RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0 --force"
RECOMMENDED_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
DISCORD_INVITE_URL = "https://discord.gg/wN7uxEVHRK"

class SetupOfScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup ofScraper")
        self.root.geometry("600x600")

        # === Attempt to load the PNG with Pillow ===
        try:
            logo_image = Image.open("starryai_0tvo7.png")
            # If needed, you can resize:
            logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo_image)
        except Exception as e:
            self.logo_img = None
            print(f"Could not load starryai_0tvo7.png: {e}")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # === Display the logo if loaded, else fallback text ===
        if self.logo_img is not None:
            logo_label = ttk.Label(main_frame, image=self.logo_img)
            logo_label.grid(row=0, column=0, columnspan=3, pady=5)
        else:
            fallback_label = ttk.Label(main_frame, text="ofScraper Setup", font=("TkDefaultFont", 14, "bold"))
            fallback_label.grid(row=0, column=0, columnspan=3, pady=5)

        # Instructions
        instructions_label = ttk.Label(
            main_frame,
            text="Click each button in numeric order:",
            font=("TkDefaultFont", 10, "bold")
        )
        instructions_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        check_python_button = ttk.Button(
            button_frame,
            text="1. Check Python Version",
            command=self.check_python_version
        )
        check_python_button.grid(row=0, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

        check_install_button = ttk.Button(
            button_frame,
            text="2. Check ofScraper Installation",
            command=self.check_ofscraper_installation
        )
        check_install_button.grid(row=0, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        install_aiolimiter_button = ttk.Button(
            button_frame,
            text="3. Install aiolimiter",
            command=self.offer_aiolimiter_installation
        )
        install_aiolimiter_button.grid(row=1, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

        update_aiohttp_button = ttk.Button(
            button_frame,
            text="4. Update aiohttp",
            command=self.offer_aiohttp_update
        )
        update_aiohttp_button.grid(row=1, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        modify_sessionmanager_button = ttk.Button(
            button_frame,
            text="5. Modify sessionmanager.py",
            command=self.modify_sessionmanager_if_needed
        )
        modify_sessionmanager_button.grid(row=2, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

        modify_config_button = ttk.Button(
            button_frame,
            text="6. Modify config.json",
            command=self.modify_ofscraper_config_if_needed
        )
        modify_config_button.grid(row=2, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        test_ofscraper_button = ttk.Button(
            button_frame,
            text="7. Test Run ofScraper",
            command=self.test_ofscraper
        )
        test_ofscraper_button.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Log of what each button does
        log_label = ttk.Label(
            main_frame,
            text="Log of what each button does:",
            font=("TkDefaultFont", 10, "bold")
        )
        log_label.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        log_text = (
            "1. Check Python Version: Checks if the current Python version is within the recommended range (3.11.x).\n"
            "2. Check ofScraper Installation: Determines if ofscraper is installed via pip, pipx, or both.\n"
            "3. Install aiolimiter: Installs or injects aiolimiter==1.1.0 depending on how ofscraper is installed.\n"
            "4. Update aiohttp: Updates aiohttp to version 3.11.6, either via pip or pipx.\n"
            "5. Modify sessionmanager.py: Patches sessionmanager.py to replace ssl=create_default_context(cafile=certifi.where()) with ssl=False.\n"
            "6. Modify config.json: Checks and modifies the config.json file for ofscraper to ensure it has the recommended settings.\n"
            "7. Test Run ofScraper: Tests running ofScraper in a new PowerShell or Command Prompt window."
        )

        log_area = tk.Text(main_frame, wrap=tk.WORD, height=10, width=70)
        log_area.insert(tk.END, log_text)
        log_area.config(state=tk.DISABLED)
        log_area.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Scrollbar for log_area
        log_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=log_area.yview)
        log_scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        log_area.config(yscrollcommand=log_scrollbar.set)

        # Status Label
        self.status_label = tk.Text(main_frame, wrap=tk.WORD, height=10, width=70)
        self.status_label.config(state=tk.DISABLED)
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        # Scrollbar for status_label
        status_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_label.yview)
        status_scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.status_label.config(yscrollcommand=status_scrollbar.set)

        self.install_type = None

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0)
        main_frame.columnconfigure(3, weight=0)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=0)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=1)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

    def update_status(self, message):
        self.status_label.config(state=tk.NORMAL)
        self.status_label.insert(tk.END, message + "\n")
        self.status_label.config(state=tk.DISABLED)
        self.status_label.see(tk.END)  # Scroll to the end of the text

    def check_python_version(self):
        major, minor, micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        message = f"You are currently using Python {major}.{minor}.{micro}"
        if (major < 3) or (major == 3 and minor < 11) or (major == 3 and minor >= 13):
            message += "\nYour Python version is not in the 3.11.x range."
            message += "\nWe recommend installing Python 3.11.6."
        else:
            message += "\nYour Python version is within the recommended range."
        self.update_status(message)

    def check_ofscraper_installation(self):
        pip_installed = False
        pipx_installed = False

        try:
            pip_show = subprocess.run(
                ["pip", "show", "ofscraper"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if "Name: ofscraper" in pip_show.stdout:
                pip_installed = True
        except FileNotFoundError:
            pass

        try:
            pipx_list = subprocess.run(
                ["pipx", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if "ofscraper" in pipx_list.stdout:
                pipx_installed = True
        except FileNotFoundError:
            pass

        if pip_installed and pipx_installed:
            self.install_type = "both"
            self.update_status("'ofscraper' appears installed with BOTH pip and pipx.")
        elif pip_installed:
            self.install_type = "pip"
            self.update_status("'ofscraper' appears installed with pip.")
        elif pipx_installed:
            self.install_type = "pipx"
            self.update_status("'ofscraper' appears installed with pipx.")
        else:
            self.install_type = None
            self.update_status("'ofscraper' not detected via pip or pipx.")

    def install_aiolimiter_via_pip(self):
        try:
            subprocess.run(
                ["pip", "install"] + RECOMMENDED_AIOLIMITER.split(),
                check=True,
                text=True
            )
            self.update_status("aiolimiter installed successfully via pip.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"An error occurred while installing via pip:\n{e}")

    def install_aiolimiter_via_pipx(self):
        try:
            subprocess.run(
                ["pipx", "inject", "ofscraper"] + RECOMMENDED_AIOLIMITER.split(),
                check=True,
                text=True
            )
            self.update_status("aiolimiter injected successfully via pipx.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"An error occurred while injecting via pipx:\n{e}")

    def offer_aiolimiter_installation(self):
        if self.install_type is None:
            self.update_status("'ofscraper' not found. We can still install aiolimiter with pip, but it may not be used.")
            choice = messagebox.askyesno("Install aiolimiter", "Do you still want to install aiolimiter via pip?")
            if choice:
                self.install_aiolimiter_via_pip()
            return

        self.update_status("We recommend installing (or injecting) aiolimiter==1.1.0 --force.")
        if self.install_type == "pip":
            choice = messagebox.askyesno("Install aiolimiter", "Install via pip now?")
            if choice:
                self.install_aiolimiter_via_pip()

        elif self.install_type == "pipx":
            choice = messagebox.askyesno("Inject aiolimiter", "Inject aiolimiter via pipx now?")
            if choice:
                self.install_aiolimiter_via_pipx()

        elif self.install_type == "both":
            options = ["Install via pip only", "Inject via pipx only", "Do both", "Skip"]
            choice = simpledialog.askinteger(
                "Install aiolimiter",
                "Select an option:\n1) Install via pip only\n2) Inject via pipx only\n3) Do both\n4) Skip",
                minvalue=1,
                maxvalue=4
            )
            if choice == 1:
                self.install_aiolimiter_via_pip()
            elif choice == 2:
                self.install_aiolimiter_via_pipx()
            elif choice == 3:
                self.install_aiolimiter_via_pip()
                self.install_aiolimiter_via_pipx()
            else:
                self.update_status("Skipping aiolimiter installation.")

    def update_aiohttp_via_pip(self):
        try:
            subprocess.run(["pip", "install", "--upgrade", "aiohttp==3.11.6"], check=True, text=True)
            self.update_status("aiohttp updated successfully via pip.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"An error occurred while updating aiohttp via pip:\n{e}")

    def update_aiohttp_via_pipx(self):
        try:
            subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.6", "--force"], check=True, text=True)
            self.update_status("aiohttp injected successfully via pipx.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"An error occurred while injecting aiohttp via pipx:\n{e}")

    def offer_aiohttp_update(self):
        if self.install_type is None:
            self.update_status("'ofscraper' not found, skipping aiohttp update.")
            return

        self.update_status("Would you like to also update aiohttp now?")
        if self.install_type == "pip":
            choice = messagebox.askyesno("Update aiohttp", "Update aiohttp with pip?")
            if choice:
                self.update_aiohttp_via_pip()

        elif self.install_type == "pipx":
            choice = messagebox.askyesno("Update aiohttp", "Update aiohttp with pipx (aiohttp==3.11.6)?")
            if choice:
                self.update_aiohttp_via_pipx()

        elif self.install_type == "both":
            options = [
                "Update aiohttp with pip",
                "Update aiohttp with pipx (aiohttp==3.11.6)",
                "Do both",
                "Skip"
            ]
            choice = simpledialog.askinteger(
                "Update aiohttp",
                "Select an option:\n1) Update aiohttp with pip\n2) Update aiohttp with pipx (aiohttp==3.11.6)\n3) Do both\n4) Skip",
                minvalue=1,
                maxvalue=4
            )
            if choice == 1:
                self.update_aiohttp_via_pip()
            elif choice == 2:
                self.update_aiohttp_via_pipx()
            elif choice == 3:
                self.update_aiohttp_via_pip()
                self.update_aiohttp_via_pipx()
            else:
                self.update_status("Skipping aiohttp update.")

    def find_pip_sitepackage_paths(self):
        paths = set(site.getsitepackages())
        user_site = site.getusersitepackages()
        if isinstance(user_site, str):
            paths.add(user_site)

        if hasattr(sys, 'prefix') and sys.prefix:
            possible_prefix_lib = os.path.join(sys.prefix, 'lib')
            if os.path.isdir(possible_prefix_lib):
                paths.add(possible_prefix_lib)

        return paths

    def find_pipx_ofscraper_sitepackage_paths(self):
        candidate_venv_paths = []

        try:
            result = subprocess.run(["pipx", "list", "--json"], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            if "venvs" in data and "ofscraper" in data["venvs"]:
                venv_path = data["venvs"]["ofscraper"].get("path")
                if venv_path and os.path.isdir(venv_path):
                    candidate_venv_paths.append(venv_path)
        except Exception:
            pass

        try:
            txt_result = subprocess.run(["pipx", "list"], capture_output=True, text=True, check=True)
            lines = txt_result.stdout.splitlines()
            for line in lines:
                if "ofscraper" in line and "Location:" in line:
                    idx = line.find("Location:")
                    if idx != -1:
                        path_str = line[idx+9:].strip()
                        if os.path.isdir(path_str):
                            candidate_venv_paths.append(path_str)
        except Exception:
            pass

        try:
            show_result = subprocess.run(["pipx", "show", "ofscraper"], capture_output=True, text=True, check=True)
            lines = show_result.stdout.splitlines()
            for line in lines:
                if "venv at" in line:
                    idx = line.find("venv at ")
                    if idx != -1:
                        path_str = line[idx+8:].strip()
                        if os.path.isdir(path_str):
                            candidate_venv_paths.append(path_str)
        except Exception:
            pass

        guess_default = os.path.expanduser("~/.local/pipx/venvs/ofscraper")
        if os.path.isdir(guess_default):
            candidate_venv_paths.append(guess_default)

        candidate_venv_paths = list(set(candidate_venv_paths))
        if not candidate_venv_paths:
            user_path = simpledialog.askstring(
                "Enter Path",
                "Unable to automatically find the pipx environment for 'ofscraper'.\n"
                "Please enter the full path to your pipx venv for ofscraper (or leave blank to skip):"
            )
            if user_path and os.path.isdir(user_path):
                candidate_venv_paths.append(user_path)

        found_paths = set()
        for venv_path in candidate_venv_paths:
            for root, dirs, files in os.walk(venv_path):
                if "site-packages" in root:
                    found_paths.add(root)
        return found_paths

    def patch_sessionmanager_in_paths(self, paths):
        old_line = "ssl=ssl.create_default_context(cafile=certifi.where()),"
        new_line = "ssl=False,"
        found_and_modified = False

        for path in paths:
            if not os.path.isdir(path):
                continue
            for root, dirs, files in os.walk(path):
                if "sessionmanager.py" in files:
                    session_file_path = os.path.join(root, "sessionmanager.py")
                    self.update_status(f"Found sessionmanager.py at: {session_file_path}")
                    try:
                        with open(session_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if old_line not in content and new_line in content:
                            self.update_status("It appears 'sessionmanager.py' has already been changed (ssl=False).")
                            return True

                        if old_line in content:
                            new_content = content.replace(old_line, new_line)
                            with open(session_file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            self.update_status("Successfully replaced ssl context with ssl=False.")
                            return True
                        else:
                            self.update_status("The expected SSL line was not found in this sessionmanager.py.")
                    except Exception as e:
                        self.update_status(f"Error modifying {session_file_path}: {e}")

        return found_and_modified

    def modify_sessionmanager_if_needed(self):
        if self.install_type is None:
            self.update_status("'ofscraper' not found at all, skipping sessionmanager patch.")
            return

        choice = messagebox.askyesno(
            "Patch sessionmanager.py",
            "Would you like to attempt to patch sessionmanager.py with 'ssl=False'?"
        )
        if not choice:
            self.update_status("Skipping sessionmanager.py modification.")
            return

        all_paths = set()
        if self.install_type in ("pip", "both"):
            all_paths |= self.find_pip_sitepackage_paths()
        if self.install_type in ("pipx", "both"):
            all_paths |= self.find_pipx_ofscraper_sitepackage_paths()

        if not all_paths:
            self.update_status("No site-package paths found for your environment(s).")
            return

        self.update_status("Searching for sessionmanager.py in these paths to patch...")
        patched = self.patch_sessionmanager_in_paths(all_paths)
        if not patched:
            self.update_status("sessionmanager.py was not modified or found.")

        # If needed, you could re-check aiohttp updates here:
        # self.offer_aiohttp_update()

    def check_key_mode_default(self, config_data):
        cdm_opts = config_data.get("cdm_options", {})
        key_mode_val = cdm_opts.get("key-mode-default")

        if key_mode_val == "manual":
            self.update_status("'key-mode-default' is already set to 'manual' in cdm_options. Nothing to change.")
        else:
            self.update_status("'key-mode-default' is NOT set to 'manual' in your cdm_options.")
            self.update_status("This means manual DRM keys will be needed to get DRM protected videos.")
            choice = messagebox.askyesno(
                "Obtain Manual DRM Keys",
                "Would you like info on obtaining manual DRM keys?"
            )
            if choice:
                self.update_status(f"See this forum post for more details on extracting L3 CDM manually:\n{DRM_KEYS_INFO_URL}")
                self.update_status(f"For more help, join our Discord: {DISCORD_INVITE_URL}")
            else:
                self.update_status("Continuing without obtaining manual DRM keys.")
                self.update_status(f"For more help, join our Discord: {DISCORD_INVITE_URL}")

    def modify_ofscraper_config_if_needed(self):
        config_path = os.path.expanduser("~/.config/ofscraper/config.json")

        choice = messagebox.askyesno(
            "Modify config.json",
            "Would you like to check (and optionally fix) ofscraper's config.json?"
        )
        if not choice:
            self.update_status("Skipping config.json modification.")
            return

        if not os.path.isfile(config_path):
            self.update_status(f"{config_path} not found.")
            create_choice = messagebox.askyesno(
                "Create config.json",
                "Would you like to create a new config.json with recommended advanced_options?"
            )
            if create_choice:
                try:
                    os.makedirs(os.path.dirname(config_path), exist_ok=True)
                    default_config = {
                        "advanced_options": {
                            "dynamic-mode-default": "generic",
                            "custom_values": {
                                "DYNAMIC_GENERIC_URL": RECOMMENDED_DYNAMIC_GENERIC_URL
                            }
                        },
                        "cdm_options": {
                            "key-mode-default": "manual"
                        }
                    }
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(default_config, f, indent=2)
                    self.update_status(f"Created new config.json at {config_path} with recommended settings.")
                    self.check_key_mode_default(default_config)
                except Exception as e:
                    self.update_status(f"Failed to create config.json: {e}")
            else:
                self.update_status("Skipping config creation.")
            return

        self.update_status(f"Found config file at {config_path}. Checking relevant advanced_options...")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            self.update_status(f"Failed to read or parse JSON from {config_path}: {e}")
            return

        adv_opts = config_data.setdefault("advanced_options", {})

        current_dmd = adv_opts.get("dynamic-mode-default")
        if current_dmd == "generic":
            self.update_status("'advanced_options.dynamic-mode-default' is already set to 'generic'.")
        else:
            self.update_status(f"'advanced_options.dynamic-mode-default' is currently '{current_dmd}'.")
            fix_choice = messagebox.askyesno(
                "Fix dynamic-mode-default",
                "Would you like to set it to 'generic'?"
            )
            if fix_choice:
                adv_opts["dynamic-mode-default"] = "generic"
                self.update_status("Will set 'advanced_options.dynamic-mode-default' to 'generic'...")

        custom_vals = adv_opts.setdefault("custom_values", {})
        current_url = custom_vals.get("DYNAMIC_GENERIC_URL")
        if current_url == RECOMMENDED_DYNAMIC_GENERIC_URL:
            self.update_status("'advanced_options.custom_values.DYNAMIC_GENERIC_URL' is already set to the recommended URL.")
        else:
            self.update_status(f"'advanced_options.custom_values.DYNAMIC_GENERIC_URL' is currently '{current_url}'.")
            fix_choice_url = messagebox.askyesno(
                "Fix DYNAMIC_GENERIC_URL",
                f"Would you like to set DYNAMIC_GENERIC_URL to '{RECOMMENDED_DYNAMIC_GENERIC_URL}'?"
            )
            if fix_choice_url:
                custom_vals["DYNAMIC_GENERIC_URL"] = RECOMMENDED_DYNAMIC_GENERIC_URL
                self.update_status("Will set 'advanced_options.custom_values.DYNAMIC_GENERIC_URL' to the recommended URL...")

        try:
            with open(config_path, "w", encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            self.update_status("Updated config.json successfully.")
            self.check_key_mode_default(config_data)
        except Exception as e:
            self.update_status(f"Failed to write changes to config.json: {e}")

    def test_ofscraper(self):
        self.update_status("Opening a new terminal window to test ofScraper...")
        try:
            if os.name == 'nt':  # Windows
                # Open PowerShell and run ofscraper
                subprocess.Popen(['powershell', '-Command', 'Start-Process', 'powershell',
                                  '-ArgumentList', '"-NoExit", "ofscraper"'])
            else:
                # On Linux (Gnome), open a new terminal
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'ofscraper; exec bash'])
        except Exception as e:
            self.update_status(f"An error occurred while opening the terminal:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupOfScraperApp(root)
    root.mainloop()
