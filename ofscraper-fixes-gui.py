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
import webbrowser
import threading

# Use Pillow for robust image loading (supports more PNG formats)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Constants for recommended versions and URLs
RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0"  # Version to fix ofscraper ending with "Finish Script"
RECOMMENDED_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
WRITTEN_GUIDE_URL = "https://example.com/drm_keys_guide"  # Replace with your written guide URL
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=MeQDCoYLTE0"  # Windows only
DISCORD_INVITE_URL = "https://discord.gg/wN7uxEVHRK"
RECOMMENDED_OS_VERSION = "3.12.9"  # Recommended version for ofscraper

def open_in_text_editor(filepath):
    """
    Open the file in a text editor.
    - Windows: uses os.startfile.
    - macOS: uses "open".
    - Linux: checks $EDITOR or common editors, then falls back to xdg-open.
    """
    if os.name == "nt":
        os.startfile(filepath)
    elif sys.platform == "darwin":
        subprocess.run(["open", filepath])
    else:
        editor_cmd = os.environ.get("EDITOR")
        if not editor_cmd:
            for candidate in ["gedit", "mousepad", "kate", "xed", "nano", "vi"]:
                if shutil.which(candidate):
                    editor_cmd = candidate
                    break
        if editor_cmd:
            subprocess.run([editor_cmd, filepath])
        else:
            subprocess.run(["xdg-open", filepath])

class SetupOfScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup ofScraper")
        self.root.geometry("615x700")
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
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
        self.embedded_proc = None  # For embedded terminal process
        self.embedded_terminal_frame = None
        self.create_widgets()

    def create_widgets(self):
        # Header
        if self.logo_img is not None:
            logo_label = ttk.Label(self.main_frame, image=self.logo_img)
            logo_label.grid(row=0, column=0, columnspan=2, pady=5)
        else:
            fallback_label = ttk.Label(self.main_frame, text="ofScraper Setup", font=("TkDefaultFont", 14, "bold"))
            fallback_label.grid(row=0, column=0, columnspan=2, pady=5)
        instructions_label = ttk.Label(self.main_frame,
                                       text="Click the buttons below to perform setup tasks:",
                                       font=("TkDefaultFont", 10, "bold"))
        instructions_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        # Buttons – Removed former buttons “Check Python Version” and “Check ofScraper Installation”
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        # Updated Button 0: "Start Here" calls combined_system_check
        start_here_button = ttk.Button(button_frame,
                                       text="Start Here",
                                       command=self.combined_system_check)
        start_here_button.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky=(tk.W, tk.E))
        finished_script_button = ttk.Button(button_frame,
                                            text="Finished Script Fix",
                                            command=self.offer_aiolimiter_installation)
        finished_script_button.grid(row=1, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))
        update_aiohttp_button = ttk.Button(button_frame,
                                           text="Update aiohttp & Fix sessionmanager.py",
                                           command=self.update_aiohttp_and_fix_sessionmanager)
        update_aiohttp_button.grid(row=1, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        auth_config_button = ttk.Button(button_frame,
                                        text="Auth Config Fix",
                                        command=self.modify_ofscraper_config_if_needed)
        auth_config_button.grid(row=2, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))
        test_run_button = ttk.Button(button_frame,
                                     text="Test Run ofscraper",
                                     command=self.test_ofscraper)
        test_run_button.grid(row=2, column=1, pady=5, padx=5, sticky=(tk.W, tk.E))
        # Log area
        log_label = ttk.Label(self.main_frame,
                              text="Log of actions:",
                              font=("TkDefaultFont", 10, "bold"))
        log_label.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.log_area = tk.Text(self.main_frame, wrap=tk.WORD, height=10, width=70)
        self.log_area.insert(tk.END, "Actions and status will appear here...\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        log_scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.log_area.yview)
        log_scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.log_area.config(yscrollcommand=log_scrollbar.set)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def update_status(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.see(tk.END)

    def combined_system_check(self):
        self.update_status("=== Combined System Check & Update ===")
        self.check_ofscraper_installation()
        version = self.get_ofscraper_version()
        self.update_status(f"Detected ofscraper version: {version}")
        if self.install_type is None:
            self.update_status("Warning: ofscraper is not installed via pip or pipx.\nPlease reinstall via pip or pipx to get version " + RECOMMENDED_OS_VERSION + ".")
            return
        if version == "unknown":
            self.update_status("Could not determine ofscraper version.")
            return
        try:
            current_version = tuple(map(int, version.split(".")))
            recommended_version = tuple(map(int, RECOMMENDED_OS_VERSION.split(".")))
        except Exception as e:
            self.update_status(f"Error parsing version numbers: {e}")
            current_version = None
        if current_version is not None and current_version < recommended_version:
            self.update_status(f"ofscraper is not at the recommended version ({RECOMMENDED_OS_VERSION}).")
            update_choice = messagebox.askyesno("Update ofscraper",
                                                 f"Your ofscraper version is {version}.\nWould you like to update to version {RECOMMENDED_OS_VERSION}?")
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
                    method = simpledialog.askinteger("Update ofscraper",
                                                     "Select update method:\n1) pip\n2) pipx\n3) Both",
                                                     minvalue=1, maxvalue=3)
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
            else:
                self.update_status("Update ofscraper not performed.")
        else:
            self.update_status("ofscraper is up-to-date!")

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
            path = shutil.which("ofscraper")
            if not path:
                self.update_status("Could not find 'ofscraper' in PATH.")
                return "unknown"
            self.update_status(f"Found 'ofscraper' at: {path}")
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    self.update_status("Error running 'ofscraper --version'.")
            except Exception as e:
                self.update_status(f"Exception when checking version: {e}")
            return "unknown"

    def offer_aiolimiter_installation(self):
        fix_dialog = messagebox.askyesno("Fix aiolimiter",
                                         "This will set aiolimiter to 1.1.0 to fix ofscraper ending with 'Finish Script'.\nDo you want to fix aiolimiter?")
        if not fix_dialog:
            self.update_status("Skipping aiolimiter fix.")
            return
        if self.install_type is None:
            self.update_status("ofscraper not found. Installing aiolimiter via pip may not be effective.")
            if messagebox.askyesno("Install aiolimiter", "Install aiolimiter via pip?"):
                self.install_aiolimiter_via_pip()
            return
        self.update_status("Installing aiolimiter==1.1.0...")
        if self.install_type in ["pip", "both"]:
            self.install_aiolimiter_via_pip()
        elif self.install_type == "pipx":
            self.install_aiolimiter_via_pipx()

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

    def update_aiohttp_and_fix_sessionmanager(self):
        explanation = (
            "This will update aiohttp to 3.11.16 and patch sessionmanager.py to fix the 'no models found' error."
        )
        messagebox.showinfo("Explanation", explanation)
        update_choice = messagebox.askyesno("Update aiohttp", "Do you want to update aiohttp to 3.11.16?")
        if update_choice:
            self.update_status("aiohttp update simulated.")
        else:
            self.update_status("Skipping aiohttp update.")
        fix_sm = messagebox.askyesno("Fix sessionmanager.py",
                                     "Do you want to patch sessionmanager.py to replace the SSL configuration?")
        if fix_sm:
            self.modify_sessionmanager_if_needed()
        else:
            self.update_status("Skipping sessionmanager.py fix.")

    def modify_ofscraper_config_if_needed(self):
        config_path = os.path.expanduser("~/.config/ofscraper/config.json")
        if not messagebox.askyesno("Auth Config Fix", "Check and fix ofscraper's config.json?"):
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
                            "custom_values": {"DYNAMIC_GENERIC_URL": RECOMMENDED_DYNAMIC_GENERIC_URL}
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
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            self.update_status(f"Failed to read config.json: {e}")
            return
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            self.update_status("Updated config.json successfully.")
            self.check_key_mode_default(config_data)
        except Exception as e:
            self.update_status(f"Failed to update config.json: {e}")
        auth_prompt = (
            "If your auth is still failing, clear your browser's cookies and cache.\n"
            "DO NOT USE the browser extension—get your auth manually and enter it into auth.json directly.\n\n"
            "Open auth.json in your default text editor?"
        )
        if messagebox.askyesno("Open auth.json", auth_prompt):
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
        cdm_opts = config_data.get("cdm_options", {})
        key_mode = cdm_opts.get("key-mode-default")
        if key_mode == "manual":
            self.update_status("'key-mode-default' is set to 'manual'.")
        else:
            self.update_status("'key-mode-default' is not set to 'manual'.")
            if messagebox.askyesno("Obtain Manual DRM Keys", "Would you like info on obtaining manual DRM keys?"):
                choice = simpledialog.askinteger("DRM Keys Info", 
                                                 "Select source:\n1. Written guide\n2. YouTube video (Windows only)",
                                                 minvalue=1, maxvalue=2)
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

    def modify_sessionmanager_if_needed(self):
        """Search for sessionmanager.py and patch its SSL configuration."""
        all_paths = set()
        if self.install_type in ("pip", "both"):
            all_paths |= self.find_pip_sitepackage_paths()
        if self.install_type in ("pipx", "both"):
            all_paths |= self.find_pipx_ofscraper_sitepackage_paths()
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

    def find_pip_sitepackage_paths(self):
        paths = set(site.getsitepackages())
        user_site = site.getusersitepackages()
        if isinstance(user_site, str):
            paths.add(user_site)
        if hasattr(sys, "prefix") and sys.prefix:
            possible_lib = os.path.join(sys.prefix, "lib")
            if os.path.isdir(possible_lib):
                paths.add(possible_lib)
        return paths

    def find_pipx_ofscraper_sitepackage_paths(self):
        candidate_paths = []
        try:
            result = subprocess.run(["pipx", "list", "--json"], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            if "venvs" in data and "ofscraper" in data["venvs"]:
                venv = data["venvs"]["ofscraper"].get("venv")
                if venv and os.path.isdir(venv):
                    candidate_paths.append(venv)
                    self.update_status(f"Found pipx venv from JSON: {venv}")
        except Exception as e:
            self.update_status(f"Error parsing pipx JSON: {e}")
        if not candidate_paths:
            if os.name == "nt":
                guess_default = os.path.join(os.environ.get("LOCALAPPDATA", ""), "pipx", "pipx", "venvs", "ofscraper")
            else:
                guess_default = os.path.expanduser("~/.local/share/pipx/venvs/ofscraper")
            if os.path.isdir(guess_default):
                candidate_paths.append(guess_default)
                self.update_status(f"Using default pipx venv path: {guess_default}")
            else:
                self.update_status(f"Default pipx venv not found: {guess_default}")
        if not candidate_paths:
            prompt = (
                "Unable to automatically find the pipx environment for 'ofscraper'.\n"
                "Please enter its full path (for example:\n"
                "Windows: C:\\Users\\cjb90\\AppData\\Local\\pipx\\pipx\\venvs\\ofscraper\n"
                "Ubuntu: /home/cjb900/.local/share/pipx/venvs/ofscraper\n"
                "or leave blank to skip):"
            )
            user_path = simpledialog.askstring("Enter Path", prompt)
            if user_path:
                user_path = os.path.normpath(user_path)
                self.update_status(f"Normalized user path: {user_path}")
                if os.path.isdir(user_path):
                    candidate_paths.append(user_path)
                    self.update_status(f"Using user-provided pipx venv path: {user_path}")
                else:
                    self.update_status("User-provided path not found or skipped.")
        found_paths = set()
        for venv in candidate_paths:
            if os.name == "nt":
                site_pkgs = os.path.join(venv, "Lib", "site-packages")
                if os.path.isdir(site_pkgs):
                    found_paths.add(site_pkgs)
                    self.update_status(f"Found site-package path: {site_pkgs}")
            else:
                pattern = os.path.join(venv, "lib", "python3.*", "site-packages")
                for p in glob.glob(pattern):
                    if os.path.isdir(p):
                        found_paths.add(p)
                        self.update_status(f"Found site-package path: {p}")
        return found_paths

    def open_ofscraper_in_new_terminal(self):
        if os.name == "nt":
            subprocess.Popen(['powershell', '-Command', 'Start-Process', 'powershell', '-ArgumentList', '"-NoExit", "ofscraper"'])
        elif sys.platform == "darwin":
            apple_script = 'tell application "Terminal" to do script "ofscraper"'
            subprocess.run(["osascript", "-e", apple_script])
        elif sys.platform.startswith("linux"):
            if shutil.which("gnome-terminal"):
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'ofscraper; exec bash'])
            elif shutil.which("xterm"):
                subprocess.Popen(['xterm', '-e', 'ofscraper'])
            else:
                self.update_status("No supported terminal emulator found.")
        else:
            self.update_status("Unsupported OS for new terminal.")

    def run_ofscraper_in_gui(self):
        window = tk.Toplevel(self.root)
        window.title("ofscraper Output (Non-interactive)")
        text_widget = tk.Text(window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill="both")
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        def run_command():
            try:
                proc = subprocess.Popen(["ofscraper"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in iter(proc.stdout.readline, ""):
                    text_widget.insert(tk.END, line)
                    text_widget.see(tk.END)
                proc.stdout.close()
                proc.wait()
            except Exception as e:
                text_widget.insert(tk.END, f"\nError running ofscraper: {e}")
        threading.Thread(target=run_command, daemon=True).start()

    def embed_terminal(self):
        """Embed an interactive terminal below the log area."""
        if self.embedded_terminal_frame is not None:
            self.term_entry.focus_set()
            return
        self.embedded_terminal_frame = ttk.Frame(self.main_frame, padding="5")
        self.embedded_terminal_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        label = ttk.Label(self.embedded_terminal_frame, text="Embedded Terminal (Interactive):", font=("TkDefaultFont", 10, "bold"))
        label.grid(row=0, column=0, columnspan=2, sticky=(tk.W))
        self.term_text = tk.Text(self.embedded_terminal_frame, wrap=tk.WORD, height=10)
        self.term_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        term_scrollbar = ttk.Scrollbar(self.embedded_terminal_frame, orient=tk.VERTICAL, command=self.term_text.yview)
        term_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.term_text.config(yscrollcommand=term_scrollbar.set)
        self.term_entry = ttk.Entry(self.embedded_terminal_frame)
        self.term_entry.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        self.term_entry.bind("<Return>", self.send_command_to_process)
        try:
            self.embedded_proc = subprocess.Popen(["ofscraper"],
                                                   stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.STDOUT,
                                                   text=True,
                                                   bufsize=1)
        except Exception as e:
            self.update_status(f"Error starting embedded terminal: {e}")
            return
        threading.Thread(target=self.read_from_process, daemon=True).start()
        self.update_status("Embedded terminal started.")

    def send_command_to_process(self, event):
        command = self.term_entry.get() + "\n"
        self.term_entry.delete(0, tk.END)
        if self.embedded_proc and self.embedded_proc.stdin:
            try:
                self.embedded_proc.stdin.write(command)
                self.embedded_proc.stdin.flush()
            except Exception as e:
                self.update_status(f"Error sending command: {e}")

    def read_from_process(self):
        while True:
            line = self.embedded_proc.stdout.readline()
            if not line:
                break
            self.root.after(0, lambda l=line: self.term_text.insert(tk.END, l))
            self.root.after(0, lambda: self.term_text.see(tk.END))

    def test_ofscraper(self):
        option = simpledialog.askinteger("Test Run ofscraper",
                                           "Enter:\n1 - Open in new terminal (interactive)\n2 - Run in GUI window (output only)\n3 - Embed interactive terminal below the log",
                                           minvalue=1, maxvalue=3)
        if option == 1:
            self.open_ofscraper_in_new_terminal()
        elif option == 2:
            self.run_ofscraper_in_gui()
        elif option == 3:
            self.embed_terminal()
        else:
            self.update_status("Invalid option for running ofscraper.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SetupOfScraperApp(root)
    root.mainloop()
