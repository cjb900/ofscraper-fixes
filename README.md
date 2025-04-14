#

       ___       ___   ______                                                 ________  _                        
     .'   `.   .' ..].' ____ \                                               |_   __  |(_)                       
    /  .-.  \ _| |_  | (___ \_| .---.  _ .--.  ,--.  _ .--.   .---.  _ .--.    | |_ \_|__   _   __  .---.  .--.  
    | |   | |'-| |-'  _.____`. / /'`\][ `/'`\]`'_\ :[ '/'`\ \/ /__\\[ `/'`\]   |  _|  [  | [ \ [  ]/ /__\\( (`\] 
    \  `-'  /  | |   | \____) || \__.  | |    // | |,| \__/ || \__., | |      _| |_    | |  > '  < | \__., `'.'. 
     `.___.'  [___]   \______.''.___.'[___]   \'-;__/| ;.__/  '.__.'[___]    |_____|  [___][__]`\_] '.__.'[\__) )
                                                    [__|                                                         






This repository contains utility scripts designed to help fix common issues with ofScraper installations and configurations. The tools provide both command-line (CLI) and graphical (GUI) interfaces to streamline the setup process.

<img src="https://github.com/user-attachments/assets/a926a573-3662-4503-b962-50b6553ff8f2" width="415" height="500"> <img src="https://github.com/user-attachments/assets/db986dba-df68-4fb0-a3bf-fdaca6a96578" width="500" height="200">


## Disclaimer

**USE AT YOUR OWN RISK**. This tool was created with the help of ChatGPT. I am not responsible for any issues, damages, or problems that this script may cause to your system, ofScraper installation, or OF account. These scripts modify files and configurations for ofscraper, and while highly unlikely could potentially lead to unintended consequences. Always backup important data before running such utilities.

This tool is provided "as is" without warranty of any kind, either expressed or implied. The user assumes the entire risk of quality, performance, and any potential issues that may arise from using these scripts.

These scripts are not officially affiliated with [ofScraper](https://github.com/datawhores/OF-Scraper/) developers unless otherwise stated.

If you have any suggestions for edits or code fixes, please open an issue or pull request.

## Features

These utilities help with:

1. **System Compatibility Check**
   - Verifies Python version (recommends Python 3.11.6)
   - Detects how ofScraper is installed (pip or pipx)
   - Checks ofScraper version (recommends 3.12.9)

2. **Installation Fixes**
   - "Finished Script" Fix: Installs aiolimiter==1.1.0 (forced) to prevent early termination
   - "No Models Found" Fix: Updates aiohttp to version 3.11.16 and patches SSL connections

3. **Configuration Management**
   - Configures `config.json` with recommended settings:
     - Sets dynamic-mode-default to "generic"
     - Configures the dynamic rules URL
     - Sets the key-mode-default to "manual" for DRM content
   - Provides guides for auth configuration and DRM key extraction

4. **Testing**
   - Opens ofScraper in a new terminal window to verify installation works

## Prerequisites

- Python 3.11.x (3.11.6 is specifically recommended)
- ofScraper installed via pip or pipx (or the script can install it for you)
- pip or pipx package managers

## Installation

1. Clone this repository or download the Python scripts:
   ```
   git clone https://github.com/yourusername/ofscraper-fixes.git
   ```
   or download the .py files directly

2. For the GUI version (optional), ensure you have tkinter and PIL/Pillow:
   ```
   pip install pillow
   ```
   
   For most Python installations, tkinter is included, but on some Linux distributions you might need to install it:
   ```
   # For Ubuntu/Debian:
   sudo apt-get install python3-tk
   ```

## Usage

### Command Line Interface (CLI)

The CLI script (`ofscraper-fixes-cli.py`) provides a menu-driven interface to fix common issues:

#### Windows

1. Open Command Prompt or PowerShell
2. Navigate to the directory containing the scripts:
   ```
   cd path\to\repository
   ```
3. Run the CLI script:
   ```
   python ofscraper-fixes-cli.py
   ```
4. Select options from the menu to perform various fixes:
   - 1. Check Python Version
   - 2. Check ofScraper Installation
   - 3. Install aiolimiter (fixes "Finished Script" issue)
   - 4. Update aiohttp (helps with "No Models Found" issue)
   - 5. Modify sessionmanager.py (fixes SSL configuration)
   - 6. Modify config.json (sets recommended configuration)
   - 7. Test Run ofScraper
   - 0. Exit

#### Linux / macOS

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
5. Follow the menu prompts as described above

### Graphical Interface (GUI)

The GUI script (`ofscraper-fixes-gui.py`) provides a user-friendly interface with buttons for each fix:

#### Windows

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
5. Use the buttons in the GUI:
   - "Start Here" - Performs a combined system check (Python version, ofScraper installation)
   - "Finished Script Fix" - Installs aiolimiter 1.1.0 to fix premature termination
   - "No Models Found Fix" - Updates aiohttp and patches sessionmanager.py's SSL configuration
   - "Auth/Config Fix & DRM Info" - Updates config.json and provides DRM guide access
   - "Test Run ofscraper" - Opens ofScraper in a new terminal window

#### Linux / macOS

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
5. Use the buttons in the GUI as described above

## Common Issues and Fixes

### "Finished Script" Error
This occurs when ofScraper ends prematurely with the message "Finish Script". The fix installs aiolimiter==1.1.0 to resolve rate limiting issues.

### "No Models Found" Error
This happens when ofScraper can't connect to the API properly. The fix:
1. Updates aiohttp to version 3.11.16
2. Patches sessionmanager.py to disable SSL verification (replaces SSL context with ssl=False)

### Authentication Problems
If you're having issues with authentication:
1. Clear your browser's cookies and cache
2. DO NOT use browser extensions for auth
3. Manually get your auth data and enter it into auth.json

### DRM Content Issues
For DRM protected videos:
1. Set key-mode-default to "manual" in config.json
2. Obtain manual DRM keys (the tool provides links to guides)

## Configuration Details

The script modifies the ofScraper configuration to:

- Set `dynamic-mode-default` to `generic` (for better compatibility)
- Set the `DYNAMIC_GENERIC_URL` to a recommended URL for dynamic rules
- Set `key-mode-default` to `manual` for CDM options

## Troubleshooting

If you encounter issues with the scripts or the fixes don't work, you can:

1. Check the logs for ofscraper to see what is failing
2. Follow the written guides in announcements on the [discord](https://discord.gg/wN7uxEVHRK)
3. Check for common issues:
   - **Tkinter not found**: Install the tkinter package for your Python installation
   - **Permission denied**: Use chmod to make the scripts executable or run with python/python3 explicitly
   - **pipx not found**: Install pipx if you want to use it (`pip install pipx`)
   - **Module not found errors**: Ensure all dependencies are installed

For additional help, you can join the Discord server: https://discord.gg/wN7uxEVHRK
