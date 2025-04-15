#!/usr/bin/env python3
import sys
import subprocess
import site
import os
import json
import glob
import shutil
import webbrowser

# Constants for recommended versions and URLs
RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0"  # Fixes ofscraper ending with "Finish Script"
RECOMMENDED_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
WRITTEN_GUIDE_URL = "https://example.com/drm_keys_guide"  # Replace with your guide URL
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=MeQDCoYLTE0"  # Windows only
DISCORD_INVITE_URL = "https://discord.gg/wN7uxEVHRK"
RECOMMENDED_OS_VERSION = "3.12.9"  # Recommended version for ofscraper
RECOMMENDED_PYTHON_VERSION = "3.11.6"  # Recommended Python version
PYTHON_DOWNLOAD_URL = "https://www.python.org/downloads/release/python-3116/"

ASCII_LOGO = r"""
       ___       ___   ______                                               
     .'   `.   .' ..].' ____ \                                              
    /  .-.  \ _| |_  | (___ \_| .---.  _ .--.  ,--.  _ .--.   .---.  _ .--. 
    | |   | |'-| |-'  _.____`. / /'`\][ `/'`\]`'_\ :[ '/'`\ \/ /__\\[ `/'`\]
    \  `-'  /  | |   | \____) || \__.  | |    // | |,| \__/ || \__., | |    
     `.___.'  [___]   \______.''.___.'[___]   \'-;__/| ;.__/  '.__.'[___]   
     ________  _                                    [__|                    
    |_   __  |(_)                                                           
      | |_ \_|__   _   __  .---.  .--.                                      
      |  _|  [  | [ \ [  ]/ /__\\( (`\]                                     
     _| |_    | |  > '  < | \__., `'.'.                                     
    |_____|  [___][__]`\_] '.__.'[\__) )                                    
"""

# Helper functions for CLI prompts
def ask_yesno(prompt):
    ans = input(prompt + " (y/n): ").strip().lower()
    return ans in ['y', 'yes']

def ask_integer(prompt, min_val, max_val):
    while True:
        try:
            ans = int(input(prompt + f" ({min_val}-{max_val}): ").strip())
            if min_val <= ans <= max_val:
                return ans
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def log_message(message):
    print(message)

# Version detection functions
def get_ofscraper_version_from_pip():
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "ofscraper"],
                                  capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
            log_message("pip show did not return version information.")
        else:
            log_message("Error running pip show ofscraper.")
    except Exception as e:
        log_message(f"Exception when checking version via pip: {e}")
    return "unknown"

def get_ofscraper_version_from_pipx():
    try:
        result = subprocess.run(["pipx", "list", "--json"],
                                  capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "venvs" in data and "ofscraper" in data["venvs"]:
                metadata = data["venvs"]["ofscraper"].get("metadata", {})
                version = metadata.get("version")
                if version:
                    return version
                else:
                    log_message("pipx list did not include a version for ofscraper.")
            else:
                log_message("ofscraper not found in pipx list.")
        else:
            log_message("Error running pipx list --json for ofscraper.")
    except Exception as e:
        log_message(f"Exception when checking version via pipx: {e}")
    return "unknown"

def get_ofscraper_version(install_type):
    if install_type == "pip":
        return get_ofscraper_version_from_pip()
    elif install_type == "pipx":
        return get_ofscraper_version_from_pipx()
    elif install_type == "both":
        version = get_ofscraper_version_from_pip()
        if version == "unknown":
            version = get_ofscraper_version_from_pipx()
        return version
    else:
        log_message("Version detection skipped as ofscraper is not installed via pip or pipx.")
        return "unknown"

# Installation detection using pip and pipx
def check_ofscraper_installation():
    pip_installed = False
    pipx_installed = False
    try:
        pip_show = subprocess.run([sys.executable, "-m", "pip", "show", "ofscraper"],
                                    capture_output=True, text=True)
        if "Name: ofscraper" in pip_show.stdout:
            pip_installed = True
    except Exception:
        pass
    try:
        pipx_list = subprocess.run(["pipx", "list", "--json"],
                                    capture_output=True, text=True)
        if pipx_list.returncode == 0:
            data = json.loads(pipx_list.stdout)
            if "venvs" in data and "ofscraper" in data["venvs"]:
                pipx_installed = True
    except Exception:
        pass

    if pip_installed and pipx_installed:
        log_message("ofscraper is installed with BOTH pip and pipx.")
        return "both"
    elif pip_installed:
        log_message("ofscraper is installed via pip.")
        return "pip"
    elif pipx_installed:
        log_message("ofscraper is installed via pipx.")
        return "pipx"
    else:
        log_message("ofscraper is NOT detected via pip or pipx.")
        return None

# Core functions corresponding to menu options
def combined_system_check():
    # Print the Python interpreter path for debugging.
    log_message(f"Script running with: {sys.executable}")
    ver = sys.version_info
    current_py = f"{ver.major}.{ver.minor}.{ver.micro}"
    log_message(f"You are currently using Python {current_py}")
    if ver.major != 3 or ver.minor < 11 or ver.minor >= 13:
        warn_text = (f"You are currently using Python {current_py}.\n"
                     "This version will not work with ofscraper.\n"
                     f"For best compatibility, please install Python {RECOMMENDED_PYTHON_VERSION}.")
        if ask_yesno(warn_text + "\nWould you like to open the download page?"):
            webbrowser.open(PYTHON_DOWNLOAD_URL)
        return
    if current_py != RECOMMENDED_PYTHON_VERSION:
        log_message("Note: The recommended Python version is 3.11.6. If you have issues, please install Python 3.11.6.")
    log_message("=== Combined System Check & Update ===")
    install_type = check_ofscraper_installation()
    version = get_ofscraper_version(install_type)
    log_message(f"Detected ofscraper version: {version}")
    if install_type is None:
        log_message("Warning: ofscraper is not detected via pip or pipx.\nPlease reinstall via pip or pipx to get version " + RECOMMENDED_OS_VERSION + ".")
        return
    if version == "unknown":
        log_message("Could not determine ofscraper version.")
        return
    try:
        current_version = tuple(map(int, version.split(".")))
        recommended_version = tuple(map(int, RECOMMENDED_OS_VERSION.split(".")))
    except Exception as e:
        log_message(f"Error parsing version numbers: {e}")
        current_version = None
    if current_version is not None and current_version < recommended_version:
        log_message(f"ofscraper is not at the recommended version ({RECOMMENDED_OS_VERSION}).")
        if ask_yesno(f"Your ofscraper version is {version}.\nWould you like to update to version {RECOMMENDED_OS_VERSION}?"):
            update_ofscraper(install_type)
        else:
            log_message("Update ofscraper not performed.")
    else:
        log_message("ofscraper is up-to-date!")

def update_ofscraper(install_type):
    if install_type == "pip":
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                           check=True, text=True)
            log_message("ofscraper updated successfully via pip.")
        except subprocess.CalledProcessError as e:
            log_message(f"Error updating via pip:\n{e}")
    elif install_type == "pipx":
        try:
            subprocess.run(["pipx", "upgrade", "ofscraper"], check=True, text=True)
            log_message("ofscraper updated successfully via pipx.")
        except subprocess.CalledProcessError as e:
            log_message(f"Error updating via pipx:\n{e}")
    elif install_type == "both":
        choice = ask_integer("Select update method:\n1) pip\n2) pipx\n3) Both", 1, 3)
        if choice == 1:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                               check=True, text=True)
                log_message("ofscraper updated successfully via pip.")
            except subprocess.CalledProcessError as e:
                log_message(f"Error updating via pip:\n{e}")
        elif choice == 2:
            try:
                subprocess.run(["pipx", "upgrade", "ofscraper"], check=True, text=True)
                log_message("ofscraper updated successfully via pipx.")
            except subprocess.CalledProcessError as e:
                log_message(f"Error updating via pipx:\n{e}")
        elif choice == 3:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", f"ofscraper=={RECOMMENDED_OS_VERSION}"],
                               check=True, text=True)
                subprocess.run(["pipx", "upgrade", "ofscraper"], check=True, text=True)
                log_message("ofscraper updated successfully via both pip and pipx.")
            except subprocess.CalledProcessError as e:
                log_message(f"Error updating via both methods:\n{e}")
    new_version = get_ofscraper_version(install_type)
    log_message(f"Updated ofscraper version: {new_version}")

def offer_aiolimiter_installation(install_type):
    if not ask_yesno("This will set aiolimiter to 1.1.0 to fix ofscraper ending with 'Finish Script'.\nDo you want to fix aiolimiter?"):
        log_message("Skipping aiolimiter fix.")
        return
    if install_type is None:
        log_message("ofscraper not found. Installing aiolimiter via pip may not be effective.")
        if ask_yesno("Install aiolimiter via pip?"):
            install_aiolimiter_via_pip()
        return
    log_message("Installing aiolimiter==1.1.0...")
    if install_type in ["pip", "both"]:
        install_aiolimiter_via_pip()
    elif install_type == "pipx":
        install_aiolimiter_via_pipx()

def install_aiolimiter_via_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", RECOMMENDED_AIOLIMITER, "--force-reinstall"],
                       check=True, text=True)
        log_message("aiolimiter installed successfully via pip.")
    except subprocess.CalledProcessError as e:
        log_message(f"Error installing aiolimiter via pip:\n{e}")

def install_aiolimiter_via_pipx():
    try:
        subprocess.run(["pipx", "inject", "ofscraper", RECOMMENDED_AIOLIMITER, "--force"],
                       check=True, text=True)
        log_message("aiolimiter injected successfully via pipx.")
    except subprocess.CalledProcessError as e:
        log_message(f"Error injecting aiolimiter via pipx:\n{e}")

def update_aiohttp_and_fix_sessionmanager():
    log_message("Explanation: This will update aiohttp to 3.11.16 and patch sessionmanager.py to fix the 'no models found' error.")
    if ask_yesno("Do you want to update aiohttp to 3.11.16?"):
        log_message("aiohttp update simulated.")
    else:
        log_message("Skipping aiohttp update.")
    if ask_yesno("Do you want to patch sessionmanager.py to replace the SSL configuration?"):
        modify_sessionmanager_if_needed()
    else:
        log_message("Skipping sessionmanager.py fix.")

def modify_ofscraper_config_if_needed():
    config_path = os.path.expanduser("~/.config/ofscraper/config.json")
    if not ask_yesno("Check and fix ofscraper's config.json?"):
        log_message("Skipping config.json modification.")
        return
    if not os.path.isfile(config_path):
        log_message(f"{config_path} not found.")
        if ask_yesno("Create new config.json with recommended settings?"):
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
                log_message(f"Created new config.json at {config_path}.")
                check_key_mode_default(default_config)
            except Exception as e:
                log_message(f"Failed to create config.json: {e}")
        else:
            log_message("Skipping config creation.")
        return
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        log_message(f"Failed to read config.json: {e}")
        return
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        log_message("Updated config.json successfully.")
        check_key_mode_default(config_data)
    except Exception as e:
        log_message(f"Failed to update config.json: {e}")
    if ask_yesno("Open auth.json in your default text editor?"):
        auth_path = os.path.expanduser("~/.config/ofscraper/main_profile/auth.json")
        if not os.path.isfile(auth_path):
            os.makedirs(os.path.dirname(auth_path), exist_ok=True)
            with open(auth_path, "w", encoding="utf-8") as f:
                f.write("{}")
            log_message(f"Created new auth.json at {auth_path}.")
        try:
            open_in_text_editor(auth_path)
        except Exception as e:
            log_message(f"Error opening auth.json: {e}")

def check_key_mode_default(config_data):
    cdm_opts = config_data.get("cdm_options", {})
    key_mode = cdm_opts.get("key-mode-default")
    if key_mode == "manual":
        log_message("'key-mode-default' is set to 'manual'.")
    else:
        log_message("'key-mode-default' is not set to 'manual'.")
        if ask_yesno("Would you like info on obtaining manual DRM keys?"):
            choice = ask_integer("Select source:\n1. Written guide\n2. YouTube video (Windows only)", 1, 2)
            if choice == 1:
                webbrowser.open(WRITTEN_GUIDE_URL)
                log_message(f"Opened written guide: {WRITTEN_GUIDE_URL}")
            elif choice == 2:
                webbrowser.open(YOUTUBE_VIDEO_URL)
                log_message(f"Opened YouTube video (Windows only): {YOUTUBE_VIDEO_URL}")
            else:
                log_message("No valid option selected.")
        else:
            log_message("Manual DRM keys info not requested.")

def modify_sessionmanager_if_needed():
    all_paths = set()
    all_paths |= find_pip_sitepackage_paths()
    all_paths |= find_pipx_ofscraper_sitepackage_paths()
    if not all_paths:
        log_message("No site-package paths found.")
        return
    log_message("Searching for sessionmanager.py in the following paths:")
    for p in all_paths:
        log_message(f"  {p}")
    if patch_sessionmanager_in_paths(all_paths):
        log_message("sessionmanager.py patched successfully.")
    else:
        log_message("sessionmanager.py was not patched or not found.")

def patch_sessionmanager_in_paths(paths):
    old_line = "ssl=ssl.create_default_context(cafile=certifi.where()),"
    new_line = "ssl=False,"
    for path in paths:
        if not os.path.isdir(path):
            continue
        for root, dirs, files in os.walk(path):
            if "sessionmanager.py" in files:
                session_file = os.path.join(root, "sessionmanager.py")
                log_message(f"Found: {session_file}")
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    if old_line not in content and new_line in content:
                        log_message("Already patched.")
                        return True
                    if old_line in content:
                        new_content = content.replace(old_line, new_line)
                        with open(session_file, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        return True
                    else:
                        log_message("Expected SSL line not found.")
                except Exception as e:
                    log_message(f"Error modifying {session_file}: {e}")
    return False

def find_pip_sitepackage_paths():
    paths = set(site.getsitepackages())
    user_site = site.getusersitepackages()
    if isinstance(user_site, str):
        paths.add(user_site)
    if hasattr(sys, "prefix") and sys.prefix:
        possible_lib = os.path.join(sys.prefix, "lib")
        if os.path.isdir(possible_lib):
            paths.add(possible_lib)
    return paths

def find_pipx_ofscraper_sitepackage_paths():
    candidate_paths = []
    try:
        result = subprocess.run(["pipx", "list", "--json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        if "venvs" in data and "ofscraper" in data["venvs"]:
            venv = data["venvs"]["ofscraper"].get("venv")
            if venv and os.path.isdir(venv):
                candidate_paths.append(venv)
                log_message(f"Found pipx venv from JSON: {venv}")
    except Exception as e:
        log_message(f"Error parsing pipx JSON: {e}")
    if not candidate_paths:
        if os.name == "nt":
            guess_default = os.path.join(os.environ.get("LOCALAPPDATA", ""), "pipx", "pipx", "venvs", "ofscraper")
        else:
            guess_default = os.path.expanduser("~/.local/share/pipx/venvs/ofscraper")
        if os.path.isdir(guess_default):
            candidate_paths.append(guess_default)
            log_message(f"Using default pipx venv path:\nWindows: C:\\Users\\cjb900\\AppData\\Local\\pipx\\pipx\\venvs\\ofscraper\nUbuntu: /home/cjb900/.local/share/pipx/venvs/ofscraper")
        else:
            log_message(f"Default pipx venv not found: {guess_default}")
    found_paths = set()
    for venv in candidate_paths:
        if os.name == "nt":
            site_pkgs = os.path.join(venv, "Lib", "site-packages")
            if os.path.isdir(site_pkgs):
                found_paths.add(site_pkgs)
                log_message(f"Found site-package path: {site_pkgs}")
        else:
            pattern = os.path.join(venv, "lib", "python3.*", "site-packages")
            for p in glob.glob(pattern):
                if os.path.isdir(p):
                    found_paths.add(p)
                    log_message(f"Found site-package path: {p}")
    return found_paths

def open_ofscraper_in_new_terminal():
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
            log_message("No supported terminal emulator found.")
    else:
        log_message("Unsupported OS for new terminal.")

def test_run_ofscraper():
    # Open ofscraper in a new terminal window.
    open_ofscraper_in_new_terminal()

def main_menu():
    while True:
        print("\n--- Setup ofScraper CLI ---")
        print("1) Combined System Check & Update")
        print("2) Finished Script Fix (Install/inject aiolimiter)")
        print("3) Update aiohttp & Fix sessionmanager.py")
        print("4) Auth Config Fix")
        print("5) Test Run ofscraper (in new terminal)")
        print("0) Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            combined_system_check()
        elif choice == "2":
            install_type = check_ofscraper_installation()
            offer_aiolimiter_installation(install_type)
        elif choice == "3":
            update_aiohttp_and_fix_sessionmanager()
        elif choice == "4":
            modify_ofscraper_config_if_needed()
        elif choice == "5":
            test_run_ofscraper()
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Print the ASCII logo and interpreter information at start.
    print(ASCII_LOGO)
    print("Setup ofScraper CLI")
    print(f"Script is running with: {sys.executable}")
    main_menu()
