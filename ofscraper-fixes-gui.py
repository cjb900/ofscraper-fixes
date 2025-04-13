#!/usr/bin/env python3
import sys
import subprocess
import site
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import glob
import shutil

# Use Pillow for robust image loading (supports more PNG formats)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Constants for recommended versions and URLs
RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0"  # Version to fix the script ending with "Finished Script"
RECOMMENDED_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
DISCORD_INVITE_URL = "https://discord.gg/wN7uxEVHRK"
RECOMMENDED_OS_VERSION = "3.12.9"  # The target version for ofscraper

class SetupOfScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup ofScraper")
        self.root.geometry("615x700")
        # Load logo if available
        if PIL_AVAILABLE:
            try:
                import urllib.request
                from io import BytesIO
                logo_url = "https://raw.githubusercontent.com/cjb900/ofscraper-fixes/refs/heads/main/starryai_0tvo7.png"
                response = urllib.request.urlopen(logo_url)
                image_data = response.read()
                logo_image = Image.open(BytesIO(image_data))
                logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(logo_image)
            except Exception as e:
                self.logo_img = None
                print(f"Could not load logo: {e}")
        else:
            self.logo_img = None

        self.install_type = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header: logo or fallback text
        if self.logo_img is not None:
            logo_label = ttk.Label(main_frame, image=self.logo_img)
            logo_label.grid(row=0, column=0, columnspan=2, pady=5)
        else:
            fallback_label = ttk.Label(main_frame, text="ofScraper Setup", font=("TkDefaultFont", 14, "bold"))
            fallback_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Instructions
        instructions_label = ttk.Label(
            main_frame,
            text="Click the buttons below to perform setup tasks:",
            font=("TkDefaultFont", 10, "bold")
        )
        instructions_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Button 0: Combined System Check & Update ofscraper
        combined_button = ttk.Button(
            button_frame,
            text="0. Combined System Check & Update ofscraper",
            command=self.combined_system_check
        )
        combined_button.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Button 1: Check Python Version
        check_python_button = ttk.Button(
            button_frame,
            text="1. Check Python Version",
            command=self.check_python_version
        )
        check_python_button.grid(row=1, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Button 2: Check ofScraper Installation
        check_install_button = ttk.Button(
            button_frame,
            text="2. Check ofScraper Installation",
            command=self.check_ofscraper_installation
        )
        check_install_button.grid(row=1, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Button 3: Install aiolimiter
        install_aiolimiter_button = ttk.Button(
            button_frame,
            text="3. Install aiolimiter",
            command=self.offer_aiolimiter_installation
        )
        install_aiolimiter_button.grid(row=2, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Button 4: Combined Update aiohttp & Fix sessionmanager.py
        update_aiohttp_session_button = ttk.Button(
            button_frame,
            text="4. Update aiohttp & Fix sessionmanager.py",
            command=self.update_aiohttp_and_fix_sessionmanager
        )
        update_aiohttp_session_button.grid(row=2, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Button 5: Modify config.json
        modify_config_button = ttk.Button(
            button_frame,
            text="5. Modify config.json",
            command=self.modify_ofscraper_config_if_needed
        )
        modify_config_button.grid(row=3, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Button 6: Test Run ofscraper
        test_ofscraper_button = ttk.Button(
            button_frame,
            text="6. Test Run ofscraper",
            command=self.test_ofscraper
        )
        test_ofscraper_button.grid(row=3, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))

        # Log Area
        log_label = ttk.Label(
            main_frame,
            text="Log of actions:",
            font=("TkDefaultFont", 10, "bold")
        )
        log_label.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        self.log_area = tk.Text(main_frame, wrap=tk.WORD, height=10, width=70)
        self.log_area.insert(tk.END, "Actions and status will appear here...\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        log_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_area.yview)
        log_scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.log_area.config(yscrollcommand=log_scrollbar.set)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def update_status(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)

    def check_python_version(self):
        major, minor, micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        message = f"You are currently using Python {major}.{minor}.{micro}\nPython interpreter: {sys.executable}"
        if (major < 3) or (major == 3 and minor < 11) or (major == 3 and minor >= 13):
            message += "\nYour Python version is not in the 3.11.x range.\nWe recommend installing Python 3.11.6."
        else:
            if micro == 6:
                message += "\nYou are on Python 3.11.6, which is ideal!"
            else:
                message += "\nYou're on Python 3.11.x (but not 3.11.6). For best results, use Python 3.11.6."
        self.update_status(message)

    def check_ofscraper_installation(self):
        pip_installed = False
        pipx_installed = False
        try:
            pip_show = subprocess.run([sys.executable, "-m", "pip", "show", "ofscraper"],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "Name: ofscraper" in pip_show.stdout:
                pip_installed = True
        except FileNotFoundError:
            pass
        try:
            pipx_list = subprocess.run(["pipx", "list", "--json"],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if pipx_list.returncode == 0:
                data = json.loads(pipx_list.stdout)
                if "venvs" in data and "ofscraper" in data["venvs"]:
                    pipx_installed = True
            else:
                pipx_list = subprocess.run(["pipx", "list"],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if "ofscraper" in pipx_list.stdout:
                    pipx_installed = True
        except Exception:
            pass
        if pip_installed and pipx_installed:
            self.install_type = "both"
            self.update_status("ofscraper is installed with BOTH pip and pipx.")
        elif pip_installed:
            self.install_type = "pip"
            self.update_status("ofscraper is installed via pip.")
        elif pipx_installed:
            self.install_type = "pipx"
            self.update_status("ofscraper is installed via pipx.")
        else:
            self.install_type = None
            self.update_status("ofscraper is NOT detected via pip or pipx.")

    def get_ofscraper_version_from_pip(self):
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "show", "ofscraper"],
                                     capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
                self.update_status("pip show did not return version information.")
            else:
                self.update_status("Error running pip show ofscraper.")
        except Exception as e:
            self.update_status(f"Exception when checking version via pip: {e}")
        return "unknown"

    def get_ofscraper_version_from_pipx(self):
        try:
            result = subprocess.run(["pipx", "runpip", "ofscraper", "show", "ofscraper"],
                                     capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
                self.update_status("pipx runpip did not return version information.")
            else:
                self.update_status("Error running pipx runpip show ofscraper.")
        except Exception as e:
            self.update_status(f"Exception when checking version via pipx: {e}")
        return "unknown"

    def get_ofscraper_version(self):
        if self.install_type == "pip":
            return self.get_ofscraper_version_from_pip()
        elif self.install_type == "pipx":
            return self.get_ofscraper_version_from_pipx()
        elif self.install_type == "both":
            version = self.get_ofscraper_version_from_pip()
            if version == "unknown":
                version = self.get_ofscraper_version_from_pipx()
            return version
        else:
            ofscraper_path = shutil.which("ofscraper")
            if not ofscraper_path:
                self.update_status("Could not find 'ofscraper' in PATH.")
                return "unknown"
            self.update_status(f"Found 'ofscraper' at: {ofscraper_path}")
            try:
                result = subprocess.run([ofscraper_path, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    self.update_status("Error running 'ofscraper --version'.")
            except Exception as e:
                self.update_status(f"Exception when checking version: {e}")
            return "unknown"

    def combined_system_check(self):
        self.update_status("=== Combined System Check & Update ===")
        self.check_python_version()
        self.check_ofscraper_installation()
        version = self.get_ofscraper_version()
        self.update_status(f"Detected ofscraper version: {version}")
        if self.install_type is None:
            self.update_status("Warning: ofscraper is not installed via pip or pipx.\nPlease reinstall via pip or pipx to get version " + RECOMMENDED_OS_VERSION + ".")
            return
        if version == "unknown":
            self.update_status("Could not determine ofscraper version.")
            return
        if version == RECOMMENDED_OS_VERSION:
            self.update_status("ofscraper is up-to-date!")
        else:
            self.update_status(f"ofscraper is not at the recommended version ({RECOMMENDED_OS_VERSION}).")
            update_choice = messagebox.askyesno(
                "Update ofscraper",
                f"Your ofscraper version is {version}.\nWould you like to update to version {RECOMMENDED_OS_VERSION}?"
            )
            if update_choice:
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
                    method = simpledialog.askinteger(
                        "Update ofscraper",
                        "Select update method:\n1) pip\n2) pipx\n3) Both",
                        minvalue=1, maxvalue=3
                    )
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
                new_version = self.get_ofscraper_version()
                self.update_status(f"Updated ofscraper version: {new_version}")

    # --- Updated Combined Method for Button 4 ---
    def update_aiohttp_and_fix_sessionmanager(self):
        # First, show an explanation dialog.
        explanation = (
            "This action will update aiohttp to version 3.11.16 and attempt to patch sessionmanager.py. "
            "These fixes help address the 'no models found' error."
        )
        messagebox.showinfo("Explanation", explanation)
        # Ask if the user wants to update aiohttp.
        update_aiohttp = messagebox.askyesno("Update aiohttp", "Do you want to update aiohttp to version 3.11.16?")
        if update_aiohttp:
            if self.install_type is None:
                self.update_status("ofscraper not detected; skipping aiohttp update.")
            else:
                if self.install_type == "pip":
                    try:
                        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "aiohttp==3.11.16"],
                                       check=True, text=True)
                        self.update_status("aiohttp updated successfully via pip.")
                    except subprocess.CalledProcessError as e:
                        self.update_status(f"Error updating aiohttp via pip:\n{e}")
                elif self.install_type == "pipx":
                    try:
                        subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.16", "--force"],
                                       check=True, text=True)
                        self.update_status("aiohttp injected successfully via pipx.")
                    except subprocess.CalledProcessError as e:
                        self.update_status(f"Error updating aiohttp via pipx:\n{e}")
                elif self.install_type == "both":
                    method = simpledialog.askinteger(
                        "Update aiohttp",
                        "Select update method:\n1) pip\n2) pipx\n3) Both",
                        minvalue=1, maxvalue=3
                    )
                    if method == 1:
                        try:
                            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "aiohttp==3.11.16"],
                                           check=True, text=True)
                            self.update_status("aiohttp updated successfully via pip.")
                        except subprocess.CalledProcessError as e:
                            self.update_status(f"Error updating aiohttp via pip:\n{e}")
                    elif method == 2:
                        try:
                            subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.16", "--force"],
                                           check=True, text=True)
                            self.update_status("aiohttp injected successfully via pipx.")
                        except subprocess.CalledProcessError as e:
                            self.update_status(f"Error updating aiohttp via pipx:\n{e}")
                    elif method == 3:
                        try:
                            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "aiohttp==3.11.16"],
                                           check=True, text=True)
                            subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.16", "--force"],
                                           check=True, text=True)
                            self.update_status("aiohttp updated successfully via both pip and pipx.")
                        except subprocess.CalledProcessError as e:
                            self.update_status(f"Error updating aiohttp via both methods:\n{e}")
        else:
            self.update_status("Skipping update of aiohttp.")

        # Regardless of the aiohttp update result, ask about sessionmanager.py patching.
        fix_sm = messagebox.askyesno(
            "Fix sessionmanager.py",
            "Do you want to attempt to patch sessionmanager.py to replace the SSL configuration? (This should fix model detection issues.)"
        )
        if fix_sm:
            self.modify_sessionmanager_if_needed()
        else:
            self.update_status("Skipping sessionmanager.py fix.")

    # --- Methods for installing aiolimiter ---
    def offer_aiolimiter_installation(self):
        fix_dialog = messagebox.askyesno(
            "Fix aiolimiter",
            "This will set the version of aiolimiter to 1.1.0 to fix the script ending with 'Finished Script'.\nDo you want to fix aiolimiter?"
        )
        if not fix_dialog:
            self.update_status("Skipping aiolimiter fix.")
            return

        if self.install_type is None:
            self.update_status("ofscraper not found. We can install aiolimiter via pip, but it may not be used unless ofscraper is installed.")
            if messagebox.askyesno("Install aiolimiter", "Install aiolimiter via pip?"):
                self.install_aiolimiter_via_pip()
            return

        self.update_status("We recommend installing (or injecting) aiolimiter==1.1.0.")
        if self.install_type == "pip":
            if messagebox.askyesno("Install aiolimiter", "Install via pip now?"):
                self.install_aiolimiter_via_pip()
        elif self.install_type == "pipx":
            if messagebox.askyesno("Inject aiolimiter", "Inject aiolimiter via pipx now?"):
                self.install_aiolimiter_via_pipx()
        elif self.install_type == "both":
            choice = simpledialog.askinteger(
                "Install aiolimiter",
                "Select an option:\n1) Install via pip only\n2) Inject via pipx only\n3) Do both\n4) Skip",
                minvalue=1, maxvalue=4
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

    def install_aiolimiter_via_pip(self):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade",
                            RECOMMENDED_AIOLIMITER, "--force-reinstall"],
                           check=True, text=True)
            self.update_status("aiolimiter installed successfully via pip.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"Error installing aiolimiter via pip:\n{e}")

    def install_aiolimiter_via_pipx(self):
        try:
            subprocess.run(["pipx", "inject", "ofscraper", RECOMMENDED_AIOLIMITER, "--force"],
                           check=True, text=True)
            self.update_status("aiolimiter injected successfully via pipx.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"Error injecting aiolimiter via pipx:\n{e}")

    # --- Method to modify sessionmanager.py ---
    def modify_sessionmanager_if_needed(self):
        if self.install_type is None:
            self.update_status("ofscraper not found; skipping sessionmanager.py patch.")
            return
        if not messagebox.askyesno("Patch sessionmanager.py", "Attempt to patch sessionmanager.py with 'ssl=False'?"):
            self.update_status("Skipping sessionmanager.py modification.")
            return
        all_paths = set()
        if self.install_type in ("pip", "both"):
            all_paths |= self.find_pip_sitepackage_paths()
        if self.install_type in ("pipx", "both"):
            all_paths |= self.find_pipx_ofscraper_sitepackage_paths()
        if not all_paths:
            self.update_status("No site-package paths found for your environment.")
            return
        self.update_status("Searching for sessionmanager.py in the following paths:")
        for p in all_paths:
            self.update_status(f"  {p}")
        patched = self.patch_sessionmanager_in_paths(all_paths)
        if not patched:
            self.update_status("sessionmanager.py was not patched or not found.")
        else:
            self.update_status("sessionmanager.py patched successfully.")

    def patch_sessionmanager_in_paths(self, paths):
        old_line = "ssl=ssl.create_default_context(cafile=certifi.where()),"
        new_line = "ssl=False,"
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
                            self.update_status("sessionmanager.py is already patched (ssl=False).")
                            return True
                        if old_line in content:
                            new_content = content.replace(old_line, new_line)
                            with open(session_file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            self.update_status("Successfully patched sessionmanager.py (ssl=False).")
                            return True
                        else:
                            self.update_status("The expected SSL line was not found in this sessionmanager.py.")
                    except Exception as e:
                        self.update_status(f"Error modifying {session_file_path}: {e}")
        return False

    # --- Method to find site-packages from a pip installation ---
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

    # --- New method to find site-packages from a pipx-installed ofscraper ---
    def find_pipx_ofscraper_sitepackage_paths(self):
        candidate_venv_paths = []
        try:
            result = subprocess.run(["pipx", "list", "--json"], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            if "venvs" in data and "ofscraper" in data["venvs"]:
                venv_path = data["venvs"]["ofscraper"].get("venv")
                if venv_path and os.path.isdir(venv_path):
                    candidate_venv_paths.append(venv_path)
                    self.update_status(f"Found pipx venv path from JSON: {venv_path}")
        except Exception as e:
            self.update_status(f"Error parsing pipx JSON: {e}")
        if not candidate_venv_paths:
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
                                self.update_status(f"Found pipx venv path from text: {path_str}")
            except Exception as e:
                self.update_status(f"Error parsing pipx text: {e}")
        if not candidate_venv_paths:
            guess_default = os.path.expanduser("~/.local/pipx/venvs/ofscraper")
            if os.path.isdir(guess_default):
                candidate_venv_paths.append(guess_default)
                self.update_status(f"Using default pipx venv path: {guess_default}")
            else:
                self.update_status(f"Default pipx venv not found: {guess_default}")
        if not candidate_venv_paths:
            # Updated prompt with example paths.
            prompt = ("Unable to automatically find the pipx environment for 'ofscraper'.\n"
                      "Please enter its full path (e.g., on Ubuntu: /home/cjb900/.local/share/pipx/venvs/ofscraper, "
                      "on Windows: C:\\Users\\cjb900\\AppData\\Local\\pipx\\pipx\\venvs\\ofscraper) or leave blank to skip:")
            user_path = simpledialog.askstring("Enter Path", prompt)
            if user_path:
                user_path = os.path.normpath(user_path)
                self.update_status(f"Normalized user path: {user_path}")
                if os.path.isdir(user_path):
                    candidate_venv_paths.append(user_path)
                    self.update_status(f"Using user-provided pipx venv path: {user_path}")
                else:
                    self.update_status("User-provided path not found or skipped.")
        found_paths = set()
        for venv_path in candidate_venv_paths:
            if os.name == "nt":
                site_pkgs = os.path.join(venv_path, "Lib", "site-packages")
                if os.path.isdir(site_pkgs):
                    found_paths.add(site_pkgs)
                    self.update_status(f"Found site-package path: {site_pkgs}")
            else:
                lib_path_pattern = os.path.join(venv_path, "lib", "python3.*", "site-packages")
                for path in glob.glob(lib_path_pattern):
                    if os.path.isdir(path):
                        found_paths.add(path)
                        self.update_status(f"Found site-package path: {path}")
        return found_paths

    # --- Method to modify config.json ---
    def modify_ofscraper_config_if_needed(self):
        config_path = os.path.expanduser("~/.config/ofscraper/config.json")
        if not messagebox.askyesno("Modify config.json", "Check and fix ofscraper's config.json?"):
            self.update_status("Skipping config.json modification.")
            return
        if not os.path.isfile(config_path):
            self.update_status(f"{config_path} not found.")
            if messagebox.askyesno("Create config.json", "Create new config.json with recommended settings?"):
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
        self.update_status(f"Found config.json at {config_path}. Checking advanced_options...")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            self.update_status(f"Failed to read or parse config.json: {e}")
            return
        adv_opts = config_data.setdefault("advanced_options", {})
        current_dmd = adv_opts.get("dynamic-mode-default")
        if current_dmd == "generic":
            self.update_status("'advanced_options.dynamic-mode-default' is set to 'generic'.")
        else:
            self.update_status(f"Current 'dynamic-mode-default' is '{current_dmd}'.")
            if messagebox.askyesno("Fix dynamic-mode-default", "Set it to 'generic'?"):
                adv_opts["dynamic-mode-default"] = "generic"
                self.update_status("Setting 'dynamic-mode-default' to 'generic'.")
        custom_vals = adv_opts.setdefault("custom_values", {})
        current_url = custom_vals.get("DYNAMIC_GENERIC_URL")
        if current_url == RECOMMENDED_DYNAMIC_GENERIC_URL:
            self.update_status("'DYNAMIC_GENERIC_URL' is set to the recommended URL.")
        else:
            self.update_status(f"Current 'DYNAMIC_GENERIC_URL' is '{current_url}'.")
            if messagebox.askyesno("Fix DYNAMIC_GENERIC_URL", f"Set it to '{RECOMMENDED_DYNAMIC_GENERIC_URL}'?"):
                custom_vals["DYNAMIC_GENERIC_URL"] = RECOMMENDED_DYNAMIC_GENERIC_URL
                self.update_status("Setting 'DYNAMIC_GENERIC_URL' to the recommended URL.")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            self.update_status("Updated config.json successfully.")
            self.check_key_mode_default(config_data)
        except Exception as e:
            self.update_status(f"Failed to update config.json: {e}")

    def check_key_mode_default(self, config_data):
        cdm_opts = config_data.get("cdm_options", {})
        key_mode_val = cdm_opts.get("key-mode-default")
        if key_mode_val == "manual":
            self.update_status("'key-mode-default' is set to 'manual' in cdm_options. Nothing to change.")
        else:
            self.update_status("'key-mode-default' is NOT set to 'manual' in your cdm_options.")
            self.update_status("Manual DRM keys are required to get DRM-protected videos.")
            choice = messagebox.askyesno("Obtain Manual DRM Keys", "Would you like info on obtaining manual DRM keys?")
            if choice:
                self.update_status(f"Forum post for manual DRM keys:\n{DRM_KEYS_INFO_URL}")
                self.update_status(f"For more help, join our Discord: {DISCORD_INVITE_URL}")
            else:
                self.update_status("Exiting as requested.")
                self.update_status(f"For more help, join our Discord: {DISCORD_INVITE_URL}")
                sys.exit(0)

    def test_ofscraper(self):
        self.update_status("Opening terminal to test ofscraper...")
        try:
            if os.name == 'nt':
                subprocess.Popen(['powershell', '-Command', 'Start-Process', 'powershell', '-ArgumentList', '"-NoExit", "ofscraper"'])
            else:
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'ofscraper; exec bash'])
        except Exception as e:
            self.update_status(f"Error opening terminal:\n{e}")

    def run(self):
        while True:
            choice = simpledialog.askinteger("Menu", "Enter a number (0=Combined Check, 1-6 for other options, 0 to exit):", minvalue=0, maxvalue=6)
            if choice is None or choice == 0:
                self.update_status("Exiting...")
                break
            elif choice == 1:
                self.check_python_version()
            elif choice == 2:
                self.check_ofscraper_installation()
            elif choice == 3:
                self.offer_aiolimiter_installation()
            elif choice == 4:
                self.update_aiohttp_and_fix_sessionmanager()
            elif choice == 5:
                self.modify_ofscraper_config_if_needed()
            elif choice == 6:
                self.test_ofscraper()
            else:
                self.update_status("Invalid option, please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupOfScraperApp(root)
    root.mainloop()
