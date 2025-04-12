#!/usr/bin/env python3

import sys
import subprocess
import site
import os
import json

RECOMMENDED_AIOLIMITER = "aiolimiter==1.1.0 --force"
RECOMMENDED_DYNAMIC_GENERIC_URL = "https://raw.githubusercontent.com/deviint/onlyfans-dynamic-rules/main/dynamicRules.json"
DRM_KEYS_INFO_URL = "https://forum.videohelp.com/threads/408031-Dumping-Your-own-L3-CDM-with-Android-Studio/page26#post2766668"
DISCORD_INVITE_URL = "https://discord.gg/wN7uxEVHRK"

def check_python_version():
    """
    Checks if Python is below 3.11 or >= 3.13.
    Suggests installing Python 3.11.6 if the condition is met.
    Displays the currently used Python version.
    """
    major, minor, micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro
    print(f"[i] You are currently using Python {major}.{minor}.{micro}")
    if (major < 3) or (major == 3 and minor < 11) or (major == 3 and minor >= 13):
        print("[!] Your Python version is not in the 3.11.x range.")
        print("[!] We recommend installing Python 3.11.6.\n")

def check_ofscraper_installation():
    """
    Determines if ofscraper is installed via pip or pipx.
    Returns one of:
      - "pip" if installed with pip
      - "pipx" if installed with pipx
      - "both" if installed with both
      - None if not found
    """
    pip_installed = False
    pipx_installed = False

    # Check pip
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
        pass  # pip not found or not in PATH

    # Check pipx
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
        pass  # pipx not found or not in PATH

    if pip_installed and pipx_installed:
        return "both"
    elif pip_installed:
        return "pip"
    elif pipx_installed:
        return "pipx"
    else:
        return None

def install_aiolimiter_via_pip():
    """
    Installs or upgrades aiolimiter==1.1.0 with pip --force.
    """
    print(f"\n[+] Installing {RECOMMENDED_AIOLIMITER} via pip...")
    try:
        subprocess.run(
            ["pip", "install"] + RECOMMENDED_AIOLIMITER.split(),
            check=True,
            text=True
        )
        print("[+] aiolimiter installed successfully via pip.\n")
    except subprocess.CalledProcessError as e:
        print("[!] An error occurred while installing via pip:\n", e)

def install_aiolimiter_via_pipx():
    """
    Injects aiolimiter==1.1.0 into ofscraper with pipx --force.
    """
    print(f"\n[+] Injecting {RECOMMENDED_AIOLIMITER} via pipx into ofscraper...")
    try:
        subprocess.run(
            ["pipx", "inject", "ofscraper"] + RECOMMENDED_AIOLIMITER.split(),
            check=True,
            text=True
        )
        print("[+] aiolimiter injected successfully via pipx.\n")
    except subprocess.CalledProcessError as e:
        print("[!] An error occurred while injecting via pipx:\n", e)

def offer_aiolimiter_installation(install_type):
    """
    Asks the user if they want to install aiolimiter==1.1.0 --force
    and performs the appropriate install action(s).
    """
    if install_type is None:
        # ofscraper not found at all
        print("\n[!] 'ofscraper' not found. We can still install aiolimiter with pip, but it may not be used.")
        choice = input("Do you still want to install aiolimiter via pip? [y/N] ").strip().lower()
        if choice == "y":
            install_aiolimiter_via_pip()
        return

    # If ofscraper is installed, ask how to proceed
    print("\n[+] We recommend installing (or injecting) aiolimiter==1.1.0 --force.")
    if install_type == "pip":
        choice = input("Install via pip now? [y/N] ").strip().lower()
        if choice == "y":
            install_aiolimiter_via_pip()

    elif install_type == "pipx":
        choice = input("Inject aiolimiter via pipx now? [y/N] ").strip().lower()
        if choice == "y":
            install_aiolimiter_via_pipx()

    elif install_type == "both":
        print("[!] 'ofscraper' appears installed with BOTH pip and pipx.")
        print("    1) Install via pip only")
        print("    2) Inject via pipx only")
        print("    3) Do both")
        print("    4) Skip")
        user_choice = input("Select an option [1/2/3/4]: ").strip()

        if user_choice == "1":
            install_aiolimiter_via_pip()
        elif user_choice == "2":
            install_aiolimiter_via_pipx()
        elif user_choice == "3":
            install_aiolimiter_via_pip()
            install_aiolimiter_via_pipx()
        else:
            print("[i] Skipping aiolimiter installation.\n")

def update_aiohttp_via_pip():
    """
    Updates aiohttp by running 'pip install --upgrade aiohttp'.
    """
    print("\n[+] Updating aiohttp via pip...")
    try:
        subprocess.run(["pip", "install", "--upgrade", "aiohttp"], check=True, text=True)
        print("[+] aiohttp updated successfully via pip.\n")
    except subprocess.CalledProcessError as e:
        print("[!] An error occurred while updating aiohttp via pip:\n", e)

def update_aiohttp_via_pipx():
    """
    Updates aiohttp by injecting a fixed version into ofscraper with pipx: 'aiohttp==3.11.6 --force'
    """
    print("\n[+] Injecting aiohttp==3.11.6 via pipx into ofscraper...")
    try:
        subprocess.run(["pipx", "inject", "ofscraper", "aiohttp==3.11.6", "--force"], check=True, text=True)
        print("[+] aiohttp injected successfully via pipx.\n")
    except subprocess.CalledProcessError as e:
        print("[!] An error occurred while injecting aiohttp via pipx:\n", e)

def offer_aiohttp_update(install_type):
    """
    Prompt the user if they'd like to update aiohttp, and perform
    the appropriate action(s) based on how ofscraper is installed.
    """
    print("[i] Would you like to also update aiohttp now?")
    if install_type == "pip":
        choice = input("Update aiohttp with pip? [y/N] ").strip().lower()
        if choice == "y":
            update_aiohttp_via_pip()

    elif install_type == "pipx":
        choice = input("Update aiohttp with pipx (aiohttp==3.11.6)? [y/N] ").strip().lower()
        if choice == "y":
            update_aiohttp_via_pipx()

    elif install_type == "both":
        print("    1) Update aiohttp with pip")
        print("    2) Update aiohttp with pipx (aiohttp==3.11.6)")
        print("    3) Do both")
        print("    4) Skip")
        user_choice = input("Select an option [1/2/3/4]: ").strip()

        if user_choice == "1":
            update_aiohttp_via_pip()
        elif user_choice == "2":
            update_aiohttp_via_pipx()
        elif user_choice == "3":
            update_aiohttp_via_pip()
            update_aiohttp_via_pipx()
        else:
            print("[i] Skipping aiohttp update.\n")

###############################################################################
#        Locating and Modifying sessionmanager.py for pip and/or pipx         #
###############################################################################

def find_pip_sitepackage_paths():
    """
    Returns a set of site-package paths for pip-based installations (system or venv).
    """
    paths = set(site.getsitepackages())
    user_site = site.getusersitepackages()
    if isinstance(user_site, str):
        paths.add(user_site)

    if hasattr(sys, 'prefix') and sys.prefix:
        possible_prefix_lib = os.path.join(sys.prefix, 'lib')
        if os.path.isdir(possible_prefix_lib):
            paths.add(possible_prefix_lib)

    return paths

def find_pipx_ofscraper_sitepackage_paths():
    """
    Attempts multiple approaches to locate the venv path for 'ofscraper' installed via pipx:

      (1) 'pipx list --json' => parse -> ...["venvs"]["ofscraper"].path
      (2) parse text from 'pipx list' for 'Location: ...'
      (3) 'pipx show ofscraper'
      (4) guess ~/.local/pipx/venvs/ofscraper
      (5) ask user for path if all else fails

    Returns a set of site-package paths for that environment. Could be empty if not found.
    """
    candidate_venv_paths = []

    # -- Attempt JSON approach
    try:
        result = subprocess.run(["pipx", "list", "--json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        if "venvs" in data and "ofscraper" in data["venvs"]:
            venv_path = data["venvs"]["ofscraper"].get("path")
            if venv_path and os.path.isdir(venv_path):
                candidate_venv_paths.append(venv_path)
    except Exception:
        pass

    # -- Attempt plain-text parse from `pipx list`
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

    # -- Attempt `pipx show ofscraper`
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

    # -- Attempt a default guess
    guess_default = os.path.expanduser("~/.local/pipx/venvs/ofscraper")
    if os.path.isdir(guess_default):
        candidate_venv_paths.append(guess_default)

    # -- If still empty, ask user
    candidate_venv_paths = list(set(candidate_venv_paths))
    if not candidate_venv_paths:
        print("[!] Unable to automatically find the pipx environment for 'ofscraper'.")
        user_path = input("Please enter the full path to your pipx venv for ofscraper (or leave blank to skip): ").strip()
        if user_path and os.path.isdir(user_path):
            candidate_venv_paths.append(user_path)

    # Convert to site-package paths
    found_paths = set()
    for venv_path in candidate_venv_paths:
        for root, dirs, files in os.walk(venv_path):
            if "site-packages" in root:
                found_paths.add(root)
    return found_paths

def patch_sessionmanager_in_paths(paths):
    """
    Given a collection of site-package paths (pip or pipx environment),
    searches for sessionmanager.py to apply the ssl=False patch.
    Returns True if we found & patched it, or it was already patched.
    """
    old_line = "ssl=ssl.create_default_context(cafile=certifi.where()),"
    new_line = "ssl=False,"
    found_and_modified = False

    for path in paths:
        if not os.path.isdir(path):
            continue
        for root, dirs, files in os.walk(path):
            if "sessionmanager.py" in files:
                session_file_path = os.path.join(root, "sessionmanager.py")
                print(f"[i] Found sessionmanager.py at: {session_file_path}")
                try:
                    with open(session_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if old_line not in content and new_line in content:
                        print("[!] It appears 'sessionmanager.py' has already been changed (ssl=False).")
                        return True

                    if old_line in content:
                        new_content = content.replace(old_line, new_line)
                        with open(session_file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print("[+] Successfully replaced ssl context with ssl=False.\n")
                        return True
                    else:
                        print("[!] The expected SSL line was not found in this sessionmanager.py.\n")
                        # We'll keep searching for more sessionmanager.py
                except Exception as e:
                    print(f"[!] Error modifying {session_file_path}: {e}\n")

    return found_and_modified

def modify_sessionmanager_if_needed(install_type):
    """
    If user agrees, tries to find and patch sessionmanager.py for the given install type(s).
    - pip only -> check pip site-packages
    - pipx only -> check pipx environment for ofscraper
    - both -> do both
    """
    if install_type is None:
        print("[i] 'ofscraper' not found at all, skipping sessionmanager patch.")
        return

    user_choice = input("Would you like to attempt to patch sessionmanager.py with 'ssl=False'? [y/N] ").strip().lower()
    if user_choice != "y":
        print("[i] Skipping sessionmanager.py modification.\n")
        return

    all_paths = set()
    if install_type in ("pip", "both"):
        all_paths |= find_pip_sitepackage_paths()
    if install_type in ("pipx", "both"):
        all_paths |= find_pipx_ofscraper_sitepackage_paths()

    if not all_paths:
        print("[!] No site-package paths found for your environment(s).")
        return

    print("[i] Searching for sessionmanager.py in these paths to patch...")
    patched = patch_sessionmanager_in_paths(all_paths)
    if not patched:
        print("[!] sessionmanager.py was not modified or found.\n")

    # Offer to update aiohttp afterwards
    offer_aiohttp_update(install_type)

###############################################################################
#                 Checking key-mode-default and config.json fixes             #
###############################################################################

def check_key_mode_default(config_data):
    """
    Checks config_data for "cdm_options" -> "key-mode-default".
    - If it *is* "manual": show a small note that it's already manual.
    - If not "manual", warns that manual DRM keys won't work in the current config
      and asks if they'd like info on obtaining manual DRM keys.
      If user says yes, show the forum link *and* mention the Discord link, then continue.
      If user says no, exit after also mentioning the Discord link.
    """
    cdm_opts = config_data.get("cdm_options", {})
    key_mode_val = cdm_opts.get("key-mode-default")

    if key_mode_val == "manual":
        print("[i] 'key-mode-default' is already set to 'manual' in cdm_options. Nothing to change.\n")
    else:
        print("[!] 'key-mode-default' is NOT set to 'manual' in your cdm_options.")
        print("[!] This means manual DRM keys will be needed to get DRM protected videos.")
        user_choice = input("Would you like info on obtaining manual DRM keys? [y/N] ").strip().lower()
        if user_choice == "y":
            print(f"\n[i] See this forum post for more details on extracting L3 CDM manually:\n{DRM_KEYS_INFO_URL}\n")
            print(f"[i] For more help, join our Discord: {DISCORD_INVITE_URL}\n")
            # Script continues, does NOT exit
        else:
            print("[!] Exiting now as requested.\n")
            print(f"[i] For more help, join our Discord: {DISCORD_INVITE_URL}\n")
            sys.exit(0)

def modify_ofscraper_config_if_needed():
    """
    Optionally checks and modifies the config.json for ofscraper, if it exists.

    We ensure:
      "advanced_options": {
        "dynamic-mode-default": "generic",
        "custom_values": {
          "DYNAMIC_GENERIC_URL": ...
        }
      }
    Then we check cdm_options -> "key-mode-default". If it's not "manual", we ask if they'd like info
    on obtaining manual DRM keys. If they say no, we exit; if they say yes, we show forum + Discord link
    and continue.
    """
    config_path = os.path.expanduser("~/.config/ofscraper/config.json")

    user_choice = input("Would you like to check (and optionally fix) ofscraper's config.json? [y/N] ").strip().lower()
    if user_choice != "y":
        print("[i] Skipping config.json modification.\n")
        return

    if not os.path.isfile(config_path):
        print(f"[!] {config_path} not found.")
        create_choice = input("Would you like to create a new config.json with recommended advanced_options? [y/N] ").strip().lower()
        if create_choice == "y":
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
                print(f"[+] Created new config.json at {config_path} with recommended settings.\n")

                # Now check the newly created data for key-mode-default
                check_key_mode_default(default_config)
            except Exception as e:
                print(f"[!] Failed to create config.json: {e}\n")
        else:
            print("[i] Skipping config creation.\n")
        return

    # If file exists, attempt to modify
    print(f"[i] Found config file at {config_path}. Checking relevant advanced_options...")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"[!] Failed to read or parse JSON from {config_path}: {e}\n")
        return

    # 1) Ensure advanced_options exists
    if "advanced_options" not in config_data:
        config_data["advanced_options"] = {}

    adv_opts = config_data["advanced_options"]

    # 2) dynamic-mode-default
    current_dmd = adv_opts.get("dynamic-mode-default")
    if current_dmd == "generic":
        print("[i] 'advanced_options.dynamic-mode-default' is already set to 'generic'.")
    else:
        print(f"[!] 'advanced_options.dynamic-mode-default' is currently '{current_dmd}'.")
        fix_choice = input("Would you like to set it to 'generic'? [y/N] ").strip().lower()
        if fix_choice == "y":
            adv_opts["dynamic-mode-default"] = "generic"
            print("[+] Will set 'advanced_options.dynamic-mode-default' to 'generic'...")

    # 3) custom_values -> DYNAMIC_GENERIC_URL
    custom_vals = adv_opts.get("custom_values")
    if not isinstance(custom_vals, dict):
        custom_vals = {}
        adv_opts["custom_values"] = custom_vals

    current_url = custom_vals.get("DYNAMIC_GENERIC_URL")
    if current_url == RECOMMENDED_DYNAMIC_GENERIC_URL:
        print("[i] 'advanced_options.custom_values.DYNAMIC_GENERIC_URL' is already set to the recommended URL.")
    else:
        print(f"[!] 'advanced_options.custom_values.DYNAMIC_GENERIC_URL' is currently '{current_url}'.")
        fix_choice_url = input(f"Would you like to set DYNAMIC_GENERIC_URL to '{RECOMMENDED_DYNAMIC_GENERIC_URL}'? [y/N] ").strip().lower()
        if fix_choice_url == "y":
            custom_vals["DYNAMIC_GENERIC_URL"] = RECOMMENDED_DYNAMIC_GENERIC_URL
            print("[+] Will set 'advanced_options.custom_values.DYNAMIC_GENERIC_URL' to the recommended URL...")

    # Attempt to save changes
    try:
        with open(config_path, "w", encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        print("[+] Updated config.json successfully.\n")
    except Exception as e:
        print(f"[!] Failed to write changes to config.json: {e}\n")
        return

    # 4) Now check cdm_options -> key-mode-default
    check_key_mode_default(config_data)

def main():
    check_python_version()

    install_type = check_ofscraper_installation()
    if install_type is None:
        print("[!] 'ofscraper' not detected via pip or pipx.")
    elif install_type == "both":
        print("[i] 'ofscraper' appears installed with BOTH pip and pipx.")
    else:
        print(f"[i] 'ofscraper' appears installed with: {install_type}")

    # Offer to install aiolimiter
    offer_aiolimiter_installation(install_type)

    # Attempt to patch sessionmanager.py
    modify_sessionmanager_if_needed(install_type)

    # Finally, offer to fix config.json
    modify_ofscraper_config_if_needed()

if __name__ == "__main__":
    main()
