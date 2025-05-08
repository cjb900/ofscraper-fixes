#!/usr/bin/env python3
# common.py - Shared functions and constants for ofScraper fix scripts

import sys
import subprocess
import site
import os
import json
import glob
import shutil
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog

# Constants for recommended versions and URLs
RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0"  # Fixes ofscraper ending with "Finish Script"
# Old URL kept for reference only - see config_fix.py for current URL
OLD_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
WRITTEN_GUIDE_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
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

def open_in_text_editor(filepath):
    """
    Open the file in a text editor.
    - Windows: uses os.startfile.
    - macOS: uses "open".
    - Linux: tries $EDITOR or common editors, then falls back to xdg-open.
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

def check_ofscraper_installation():
    """
    Check if ofscraper is installed via pip, pipx, or both.
    Returns: "pip", "pipx", "both", or None if not installed.
    """
    pip_installed = False
    pipx_installed = False
    try:
        pip_show = subprocess.run([sys.executable, "-m", "pip", "show", "ofscraper"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "Name: ofscraper" in pip_show.stdout:
            pip_installed = True
    except Exception:
        pass
    try:
        pipx_list = subprocess.run(["pipx", "list", "--json"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if pipx_list.returncode == 0:
            data = json.loads(pipx_list.stdout)
            if "venvs" in data and "ofscraper" in data["venvs"]:
                pipx_installed = True
    except Exception:
        pass
    
    if pip_installed and pipx_installed:
        return "both"
    elif pip_installed:
        return "pip"
    elif pipx_installed:
        return "pipx"
    else:
        return None

def get_ofscraper_version_from_pip():
    """Get the ofscraper version from pip."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "ofscraper"],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "unknown"

def get_ofscraper_version_from_pipx():
    """Get the ofscraper version from pipx."""
    # First attempt: use pipx list --json.
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
    except Exception:
        pass
    
    # Fallback: use pipx runpip ofscraper show ofscraper.
    try:
        result = subprocess.run(["pipx", "runpip", "ofscraper", "show", "ofscraper"],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":",1)[1].strip()
    except Exception:
        pass
    
    return "unknown"

def get_ofscraper_version(install_type):
    """Get the ofscraper version based on install type."""
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
        return "unknown"

def find_pip_sitepackage_paths():
    """Find all possible site-package paths for pip installations."""
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
    """Find site-package paths for pipx ofscraper installation."""
    candidate_paths = []
    try:
        result = subprocess.run(["pipx", "list", "--json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        if "venvs" in data and "ofscraper" in data["venvs"]:
            venv = data["venvs"]["ofscraper"].get("venv")
            if venv and os.path.isdir(venv):
                candidate_paths.append(venv)
    except Exception:
        pass
    
    if not candidate_paths:
        if os.name == "nt":
            guess_default = os.path.join(os.environ.get("LOCALAPPDATA", ""), "pipx", "pipx", "venvs", "ofscraper")
        else:
            guess_default = os.path.expanduser("~/.local/share/pipx/venvs/ofscraper")
        if os.path.isdir(guess_default):
            candidate_paths.append(guess_default)
    
    found_paths = set()
    for venv in candidate_paths:
        if os.name == "nt":
            site_pkgs = os.path.join(venv, "Lib", "site-packages")
            if os.path.isdir(site_pkgs):
                found_paths.add(site_pkgs)
        else:
            pattern = os.path.join(venv, "lib", "python3.*", "site-packages")
            for p in glob.glob(pattern):
                if os.path.isdir(p):
                    found_paths.add(p)
    return found_paths

def get_ofscraper_executable_path(install_type):
    """Get the path to the ofscraper executable based on installation type"""
    # For development testing - uncomment to debug
    # print(f"Finding ofscraper for install type: {install_type}")
    
    # First check if python -m ofscraper works
    python_module_cmd = [sys.executable, "-m", "ofscraper"]
    try:
        # Just test if it can be imported, don't actually run it
        result = subprocess.run([sys.executable, "-c", "import ofscraper; print(ofscraper.__file__)"], 
                               capture_output=True, text=True)
        if result.returncode == 0 and 'ofscraper' in result.stdout:
            # If it can be imported, use python -m ofscraper
            return python_module_cmd
    except Exception:
        pass
    
    # Second approach: Try to get the specific entry point script location
    if install_type == "pip":
        # For pip installations, try to get the path using pip show
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "show", "-f", "ofscraper"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # First look for entry points or scripts
                for line in result.stdout.splitlines():
                    if ("bin/ofscraper" in line or "Scripts\\ofscraper" in line or 
                        "Scripts\\ofscraper.exe" in line):
                        # Extract the path
                        path = line.strip()
                        # For Windows, we need the .exe extension
                        if os.name == "nt" and not path.endswith(".exe"):
                            path = path + ".exe"
                        # Check if this is a relative path within site-packages
                        if not os.path.isabs(path):
                            # Get the installation location 
                            for location_line in result.stdout.splitlines():
                                if location_line.startswith("Location:"):
                                    location = location_line.split(":", 1)[1].strip()
                                    # Try to construct full path
                                    potential_paths = [
                                        os.path.join(location, path),
                                        os.path.join(location, "..", "..", path)
                                    ]
                                    for test_path in potential_paths:
                                        if os.path.exists(test_path):
                                            return test_path
                
                # If we can't find the entry point, fall back to Python module
                return python_module_cmd
        except Exception as e:
            print(f"Error finding pip install: {e}")
            pass
            
    elif install_type == "pipx":
        # For pipx installations, first try to find the executable directly in binary directory
        try:
            # Check common binary locations for pipx installs
            if os.name == "nt":  # Windows
                user_bin_dir = os.path.expanduser("~\\.local\\bin")
                pipx_bin_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "pipx", "bin")
                locations = [user_bin_dir, pipx_bin_dir]
            else:  # Unix-like
                locations = [
                    os.path.expanduser("~/.local/bin"),
                    "/usr/local/bin"
                ]
                
            for location in locations:
                exe_name = "ofscraper.exe" if os.name == "nt" else "ofscraper"
                full_path = os.path.join(location, exe_name)
                if os.path.exists(full_path):
                    return full_path
            
            # If we can't find it directly, try pipx info
            result = subprocess.run(["pipx", "list", "--json"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "venvs" in data and "ofscraper" in data["venvs"]:
                    # First try the 'app' paths
                    if 'apps' in data["venvs"]["ofscraper"]:
                        apps = data["venvs"]["ofscraper"]["apps"]
                        if isinstance(apps, list) and 'ofscraper' in apps:
                            for bin_dir in locations:
                                path = os.path.join(bin_dir, "ofscraper")
                                if os.name == "nt":
                                    path += ".exe"
                                if os.path.exists(path):
                                    return path
                    
                    # Next try the Python path approach
                    venv_info = data["venvs"]["ofscraper"]
                    if "python" in venv_info:
                        python_path = venv_info["python"]
                        bin_dir = os.path.dirname(python_path)
                        # Construct the path
                        ofscraper_exe = os.path.join(bin_dir, "ofscraper")
                        if os.name == "nt" and not ofscraper_exe.endswith(".exe"):
                            ofscraper_exe += ".exe"
                        if os.path.exists(ofscraper_exe):
                            return ofscraper_exe
                        
                        # If executable not found, try running as module
                        return [python_path, "-m", "ofscraper"]
        except Exception as e:
            print(f"Error finding pipx install: {e}")
            pass
    
    # Third approach: For both install types, try shutil.which to check PATH
    ofscraper_in_path = shutil.which("ofscraper")
    if ofscraper_in_path:
        return ofscraper_in_path
            
    # Last resort: fallback to basic command and hope PATH is correct
    return ["python", "-m", "ofscraper"] if install_type else "ofscraper"

def open_ofscraper_in_new_terminal(install_type=None):
    """Open ofscraper in a new terminal window."""
    # Get the path to the ofscraper executable
    ofscraper_cmd = get_ofscraper_executable_path(install_type)
    
    # Prepare the command to run
    if isinstance(ofscraper_cmd, list):
        cmd_str = " ".join(ofscraper_cmd)
    else:
        cmd_str = ofscraper_cmd
    
    if os.name == "nt":
        # Use execution policy bypass to avoid PowerShell profile issues
        ps_args = f'"-ExecutionPolicy", "Bypass", "-NoProfile", "-NoExit", "-Command", "{cmd_str}"'
        subprocess.Popen(['powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', 
                         f'Start-Process powershell -ArgumentList {ps_args}'])
    elif sys.platform == "darwin":
        apple_script = f'tell application "Terminal" to do script "{cmd_str}"'
        subprocess.run(["osascript", "-e", apple_script])
    elif sys.platform.startswith("linux"):
        if shutil.which("gnome-terminal"):
            if isinstance(ofscraper_cmd, list):
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{" ".join(ofscraper_cmd)}; exec bash'])
            else:
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{ofscraper_cmd}; exec bash'])
        elif shutil.which("xterm"):
            if isinstance(ofscraper_cmd, list):
                subprocess.Popen(['xterm', '-e', f'{" ".join(ofscraper_cmd)}'])
            else:
                subprocess.Popen(['xterm', '-e', f'{ofscraper_cmd}'])
        else:
            return False
    else:
        return False
    return True