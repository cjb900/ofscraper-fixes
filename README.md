# ofScraper Fixes

This repository contains utility scripts designed to help fix common issues with ofScraper installations and configurations. The tools provide both command-line (CLI) and graphical (GUI) interfaces to streamline the setup process.

## Overview

These scripts help with:

1. Checking Python version compatibility (recommends Python 3.11.x)
2. Detecting how ofScraper is installed (pip or pipx)
3. Installing/updating dependencies:
   - Installing aiolimiter==1.1.0 (forced)
   - Updating aiohttp to version 3.11.6
4. Patching `sessionmanager.py` by replacing SSL context creation with `ssl=False`
5. Configuring `config.json` with recommended settings:
   - Setting dynamic-mode-default to "generic"
   - Configuring the dynamic rules URL
   - Setting the key-mode-default to "manual" for DRM content
6. Testing the ofScraper installation

## Prerequisites

- Python 3.11.x (3.11.6 is specifically recommended)
- ofScraper installed via pip or pipx

## Usage

### Windows

#### Command Line Interface (CLI)

1. Open Command Prompt or PowerShell
2. Navigate to the directory containing the scripts:
   ```
   cd path\to\repository
   ```
3. Run the CLI script:
   ```
   python ofscraper-fixes-cli.py
   ```
4. Follow the prompts to complete the configuration

#### Graphical Interface (GUI)

1. Right-click on `ofscraper-fixes-gui.py` and select "Open with Python" OR
2. Open Command Prompt or PowerShell
3. Navigate to the directory containing the scripts:
   ```
   cd path\to\repository
   ```
4. Run the GUI script:
   ```
   python ofscraper-fixes-gui.py
   ```
5. Follow the instructions in the GUI, clicking each button in numerical order

### Linux

#### Command Line Interface (CLI)

1. Open a terminal
2. Navigate to the directory containing the scripts:
   ```
   cd path/to/repository
   ```
3. Make the script executable (if needed):
   ```
   chmod +x ofscraper-fixes-cli.py
   ```
4. Run the CLI script:
   ```
   ./ofscraper-fixes-cli.py
   ```
   or
   ```
   python3 ofscraper-fixes-cli.py
   ```
5. Follow the prompts to complete the configuration

#### Graphical Interface (GUI)

1. Open a terminal
2. Navigate to the directory containing the scripts:
   ```
   cd path/to/repository
   ```
3. Make the script executable (if needed):
   ```
   chmod +x ofscraper-fixes-gui.py
   ```
4. Run the GUI script:
   ```
   ./ofscraper-fixes-gui.py
   ```
   or
   ```
   python3 ofscraper-fixes-gui.py
   ```
5. Follow the instructions in the GUI, clicking each button in numerical order

## GUI Requirements

The GUI script uses Tkinter, which should be included with most Python installations. For better image support, it will attempt to use PIL/Pillow if available. If you want to enable image support:

```
pip install pillow
```

## What the Scripts Do

1. **Check Python Version**: Verifies that you're using Python 3.11.x
2. **Check ofScraper Installation**: Determines if ofScraper is installed via pip, pipx, or both
3. **Install aiolimiter**: Installs or injects aiolimiter==1.1.0 to help with rate limiting
4. **Update aiohttp**: Updates the aiohttp library to resolve compatibility issues
5. **Modify sessionmanager.py**: Patches the SSL configuration to fix connection issues
6. **Modify config.json**: Updates configuration to use recommended settings for dynamic rules and CDM options
7. **Test Run ofScraper**: Opens a new terminal window to test if ofScraper runs correctly

## Configuration Changes

The script modifies the ofScraper configuration to:

- Set `dynamic-mode-default` to `generic`
- Set the `DYNAMIC_GENERIC_URL` to a recommended URL for dynamic rules
- Set `key-mode-default` to `manual` for CDM options

## Troubleshooting

If you encounter issues with DRM-protected content, the script can provide information about obtaining manual DRM keys.

For additional help, you can join the Discord server: https://discord.gg/wN7uxEVHRK

## Disclaimer

**USE AT YOUR OWN RISK**. I am not responsible for any issues, damages, or problems that this script may cause to your system, ofScraper installation, or account. These scripts modify system files and configurations, which could potentially lead to unintended consequences. Always backup important data before running such utilities.

This tool is provided "as is" without warranty of any kind, either expressed or implied. The user assumes the entire risk of quality, performance, and any potential issues that may arise from using these scripts.

These scripts are not officially affiliated with ofScraper developers unless otherwise stated.
