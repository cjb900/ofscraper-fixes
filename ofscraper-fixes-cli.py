#!/usr/bin/env python3
import sys
import subprocess
import site
import os
import json
import glob
import shutil  # To check for existence of commands

# Recommended dependencies and URLs.
RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0 --force"
RECOMMENDED_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
DISCORD_INVITE_URL = "https://discord.gg/wN7uxEVHRK"


def ask_yes_no(prompt):
    """Prompt user with a yes/no question. Returns True for yes, False for no."""
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        elif ans in ("n", "no"):
            return False
        else:
            print("Please answer with 'y' or 'n'.")


def ask_integer(prompt, min_value=None, max_value=None):
    """Prompt the user to enter an integer. Optionally enforce min and max."""
    while True:
        try:
            ans = int(input(f"{prompt}: ").strip())
            if (min_value is not None and ans < min_value) or (max_value is not None and ans > max_value):
                print(f"Please enter an integer between {min_value} and {max_value}.")
            else:
                return ans
        except ValueError:
            print("Invalid integer; please try again.")


def ask_string(prompt):
    """Prompt user to enter a string."""
    return input(f"{prompt}: ").strip()


BANNER = r"""
                      ___   __                                          
 _____ _____ _____   / _ \ / _|___  ___ _ __ __ _ _ __   ___ _ __       
|_____|_____|_____| | | | | |_/ __|/ __| '__/ _` | '_ \ / _ \ '__|      
|_____|_____|_____| | |_| |  _\__ \ (__| | | (_| | |_) |  __/ |         
                     \___/|_| |___/\___|_|  \__,_| .__/ \___|_|         
 ____       _                  ____ _     ___   _|_|__                  
/ ___|  ___| |_ _   _ _ __    / ___| |   |_ _| |  \/  | ___ _ __  _   _ 
\___ \ / _ \ __| | | | '_ \  | |   | |    | |  | |\/| |/ _ \ '_ \| | | |
 ___) |  __/ |_| |_| | |_) | | |___| |___ | |  | |  | |  __/ | | | |_| |
|____/ \___|\__|\__,_| .__/   \____|_____|___| |_|  |_|\___|_| |_|\__,_|
|_____|_____|_____|  |_|                                                
|_____|_____|_____|                                                  
"""


class SetupOfScraperCLI:
    def __init__(self):
        self.install_type = None

    def update_status(self, message):
        print(message)

    def check_python_version(self):
        major, minor, micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        message = f"You are currently using Python {major}.{minor}.{micro}"
        if (major < 3) or (major == 3 and minor < 11) or (major == 3 and minor >= 13):
            message += "\nYour Python version is not in the 3.11.x range."
            message += "\nWe recommend installing Python 3.11.6."
        else:
            if micro == 6:
                message += "\nYou are on Python 3.11.6, which is fully recommended!"
            else:
                message += "\nYou're on Python 3.11.x (but not 3.11.6)."
                message += "\nIf you run into Python-related issues, we recommend trying Python 3.11.6."
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
                ["pipx", "list", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if pipx_list.returncode == 0:
                data = json.loads(pipx_list.stdout)
                if "venvs" in data and "ofscraper" in data["venvs"]:
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
            if ask_yes_no("ofscraper is not detected. Would you like to install it now?"):
                method_choice = ask_integer("How would you like to install ofscraper?\n1) pip\n2) pipx", 1, 2)
                if method_choice == 1:
                    try:
                        subprocess.run(["pip", "install", "ofscraper"], check=True, text=True)
                        self.update_status("ofscraper installed successfully via pip.")
                        self.check_ofscraper_installation()
                        return
                    except subprocess.CalledProcessError as e:
                        self.update_status(f"Error installing ofscraper via pip:\n{e}")
                elif method_choice == 2:
                    if shutil.which("pipx") is None:
                        self.update_status("pipx not found in your system PATH. Please install pipx or choose pip instead.")
                    else:
                        try:
                            subprocess.run(["pipx", "install", "ofscraper"], check=True, text=True)
                            self.update_status("ofscraper installed successfully via pipx.")
                            self.check_ofscraper_installation()
                            return
                        except subprocess.CalledProcessError as e:
                            self.update_status(f"Error installing ofscraper via pipx:\n{e}")
            else:
                self.update_status("Skipping ofscraper installation.")

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
        if shutil.which("pipx") is None:
            self.update_status("pipx not found in your system PATH. Cannot inject aiolimiter via pipx.")
            return
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
            self.update_status(
                "'ofscraper' not found. We can still install aiolimiter with pip, "
                "but it may not be used unless ofscraper is installed."
            )
            if ask_yes_no("Do you still want to install aiolimiter via pip?"):
                self.install_aiolimiter_via_pip()
            return

        self.update_status("We recommend installing (or injecting) aiolimiter==1.1.0 --force.")
        if self.install_type == "pip":
            if ask_yes_no("Install via pip now?"):
                self.install_aiolimiter_via_pip()
        elif self.install_type == "pipx":
            if ask_yes_no("Inject aiolimiter via pipx now?"):
                self.install_aiolimiter_via_pipx()
        elif self.install_type == "both":
            choice = ask_integer("Select an option:\n1) Install via pip only\n2) Inject via pipx only\n3) Do both\n4) Skip", 1, 4)
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
            subprocess.run(["pip", "install", "--upgrade", "aiohttp==3.11.16"], check=True, text=True)
            self.update_status("aiohttp updated successfully via pip.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"An error occurred while updating aiohttp via pip:\n{e}")

    def update_aiohttp_via_pipx(self):
        if shutil.which("pipx") is None:
            self.update_status("pipx not found in your system PATH. Cannot update aiohttp via pipx.")
            return
        try:
            subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.16", "--force"], check=True, text=True)
            self.update_status("aiohttp injected successfully via pipx.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"An error occurred while injecting aiohttp via pipx:\n{e}")

    def offer_aiohttp_update(self):
        if self.install_type is None:
            self.update_status("'ofscraper' not found, skipping aiohttp update.")
            return

        self.update_status("Would you like to also update aiohttp now?")
        if self.install_type == "pip":
            if ask_yes_no("Update aiohttp with pip?"):
                self.update_aiohttp_via_pip()
        elif self.install_type == "pipx":
            if ask_yes_no("Update aiohttp with pipx (aiohttp==3.11.16)?"):
                self.update_aiohttp_via_pipx()
        elif self.install_type == "both":
            choice = ask_integer("Select an option:\n1) Update aiohttp with pip\n2) Update aiohttp with pipx (aiohttp==3.11.16)\n3) Do both\n4) Skip", 1, 4)
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
                venv_path = data["venvs"]["ofscraper"].get("venv")
                if venv_path and os.path.isdir(venv_path):
                    candidate_venv_paths.append(venv_path)
                    self.update_status(f"Found pipx venv path from JSON: {venv_path}")
                else:
                    self.update_status(f"No valid venv path found in JSON: {venv_path}")
            else:
                self.update_status("No ofscraper venv found in pipx list JSON.")
        except Exception as e:
            self.update_status(f"Error parsing pipx list JSON: {e}")

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
                                self.update_status(f"Found pipx venv path from text output: {path_str}")
                            else:
                                self.update_status(f"Invalid path found in text output: {path_str}")
            except Exception as e:
                self.update_status(f"Error parsing pipx list text output: {e}")

        if not candidate_venv_paths:
            guess_default = os.path.expanduser("~/AppData/Local/pipx/venvs/ofscraper")
            if os.path.isdir(guess_default):
                candidate_venv_paths.append(guess_default)
                self.update_status(f"Using default pipx venv path: {guess_default}")
            else:
                self.update_status(f"Default pipx venv path not found: {guess_default}")

        if not candidate_venv_paths:
            user_path = ask_string("Unable to automatically find the pipx environment for 'ofscraper'.\nPlease enter the full path to your pipx venv for ofscraper (or leave blank to skip)")
            if user_path and os.path.isdir(user_path):
                candidate_venv_paths.append(user_path)
                self.update_status(f"Using user-provided pipx venv path: {user_path}")
            else:
                self.update_status(f"User-provided path not found: {user_path}")

        found_paths = set()
        for venv_path in candidate_venv_paths:
            if os.path.basename(os.path.normpath(venv_path)).lower() == "site-packages":
                found_paths.add(venv_path)
                self.update_status(f"Candidate path is already a site-packages directory: {venv_path}")
                continue

            if os.name == "nt":
                site_pkgs = os.path.join(venv_path, "Lib", "site-packages")
                if os.path.isdir(site_pkgs):
                    found_paths.add(site_pkgs)
                    self.update_status(f"Found site-package path: {site_pkgs}")
                else:
                    self.update_status(f"No site-package paths found in {venv_path}")
            else:
                lib_path_pattern = os.path.join(venv_path, "lib", "python3.*", "site-packages")
                for path in glob.glob(lib_path_pattern):
                    if os.path.isdir(path):
                        found_paths.add(path)
                        self.update_status(f"Found site-package path: {path}")
                if not found_paths:
                    self.update_status(f"No site-package paths found in {venv_path}")

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

        if not ask_yes_no("Would you like to attempt to patch sessionmanager.py with 'ssl=False'?"):
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

    def check_key_mode_default(self, config_data):
        cdm_opts = config_data.get("cdm_options", {})
        key_mode_val = cdm_opts.get("key-mode-default")
        if key_mode_val == "manual":
            self.update_status("'key-mode-default' is already set to 'manual' in cdm_options. Nothing to change.")
        else:
            self.update_status("'key-mode-default' is NOT set to 'manual' in your cdm_options.")
            self.update_status("This means manual DRM keys will be needed to get DRM protected videos.")
            if ask_yes_no("Would you like info on obtaining manual DRM keys?"):
                self.update_status(f"See this forum post for more details on extracting L3 CDM manually:\n{DRM_KEYS_INFO_URL}")
                self.update_status(f"For more help, join our Discord: {DISCORD_INVITE_URL}")
            else:
                self.update_status("Continuing without obtaining manual DRM keys.")
                self.update_status(f"For more help, join our Discord: {DISCORD_INVITE_URL}")

    def modify_ofscraper_config_if_needed(self):
        config_path = os.path.expanduser("~/.config/ofscraper/config.json")
        if not ask_yes_no("Would you like to check (and optionally fix) ofscraper's config.json?"):
            self.update_status("Skipping config.json modification.")
            return
        if not os.path.isfile(config_path):
            self.update_status(f"{config_path} not found.")
            if ask_yes_no("Would you like to create a new config.json with recommended advanced_options?"):
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
            if ask_yes_no("Would you like to set it to 'generic'?"):
                adv_opts["dynamic-mode-default"] = "generic"
                self.update_status("Will set 'advanced_options.dynamic-mode-default' to 'generic'...")
        custom_vals = adv_opts.setdefault("custom_values", {})
        current_url = custom_vals.get("DYNAMIC_GENERIC_URL")
        if current_url == RECOMMENDED_DYNAMIC_GENERIC_URL:
            self.update_status("'advanced_options.custom_values.DYNAMIC_GENERIC_URL' is already set to the recommended URL.")
        else:
            self.update_status(f"'advanced_options.custom_values.DYNAMIC_GENERIC_URL' is currently '{current_url}'.")
            if ask_yes_no(f"Would you like to set DYNAMIC_GENERIC_URL to '{RECOMMENDED_DYNAMIC_GENERIC_URL}'?"):
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
        self.update_status("Attempting to open a new terminal window to test ofScraper...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['powershell', '-Command', 'Start-Process', 'powershell',
                                  '-ArgumentList', '"-NoExit", "ofscraper"'])
            else:
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'ofscraper; exec bash'])
        except Exception as e:
            self.update_status(f"An error occurred while opening the terminal:\n{e}")

    def run(self):
        while True:
            # Print the ASCII banner instead of a simple menu header.
            print(BANNER)
            print("1. Check Python Version")
            print("2. Check ofScraper Installation")
            print("3. Install aiolimiter")
            print("4. Update aiohttp")
            print("5. Modify sessionmanager.py")
            print("6. Modify config.json")
            print("7. Test Run ofScraper")
            print("0. Exit")
            choice = ask_integer("Select an option", 0, 7)
            if choice == 0:
                self.update_status("Exiting...")
                break
            elif choice == 1:
                self.check_python_version()
            elif choice == 2:
                self.check_ofscraper_installation()
            elif choice == 3:
                self.offer_aiolimiter_installation()
            elif choice == 4:
                self.offer_aiohttp_update()
            elif choice == 5:
                self.modify_sessionmanager_if_needed()
            elif choice == 6:
                self.modify_ofscraper_config_if_needed()
            elif choice == 7:
                self.test_ofscraper()
            else:
                self.update_status("Invalid option, please try again.")


if __name__ == "__main__":
    cli = SetupOfScraperCLI()
    cli.run()
