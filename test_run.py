#!/usr/bin/env python3
# test_run.py - Open ofscraper in a new terminal for testing

import os
import sys
import tkinter as tk
import threading
import subprocess
import site
import glob
import shutil
import tempfile

# Import shared components
from common import (
    check_ofscraper_installation,
)

class TestRunTool:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        
    def run(self):
        """Run the test tool to open ofscraper in a new terminal"""
        self.update_status("=== Test Run Tool ===")
        
        # Check if development version exists in current directory
        if os.path.exists(os.path.join(os.getcwd(), "ofscraper")) or os.path.exists(os.path.join(os.getcwd(), "ofscraper.py")):
            self.update_status("WARNING: Development version of ofScraper detected in current directory!")
            self.update_status("This may interfere with running the installed version.")
        
        # Determine installation type
        install_type = check_ofscraper_installation()
        if install_type is None:
            self.update_status("Warning: ofScraper is not detected via pip or pipx.")
            if not self.try_direct_install():
                self.update_status("Could not find or install ofScraper. Please install it using pip or pipx first.")
                return
        else:
            self.update_status(f"Using ofScraper installed via {install_type}.")
        
        # Find the pip/pipx executable directly - most reliable approach
        pip_path = self.get_pip_installed_script()
        pipx_path = self.get_pipx_installed_script() 
        
        # Prefer pipx over pip if both are available (pipx is more likely to be a proper install)
        if pipx_path:
            self.update_status(f"Found pipx installed script: {pipx_path}")
            success = self.launch_in_terminal([pipx_path])
        elif pip_path:
            self.update_status(f"Found pip installed script: {pip_path}")
            success = self.launch_in_terminal([pip_path])
        else:
            # Fall back to Python module approach
            self.update_status("Could not find direct executable. Trying module approach...")
            module_cmd = self.find_installed_ofscraper_module()
            
            if module_cmd:
                self.update_status(f"Using Python module approach: {' '.join(module_cmd)}")
                success = self.launch_in_terminal(module_cmd)
            else:
                self.update_status("Could not determine how to run ofScraper. Trying generic command...")
                success = self.launch_in_terminal("ofscraper")
        
        if not success:
            self.update_status("Failed to launch. Falling back to non-interactive mode.")
            self.run_ofscraper_in_gui("ofscraper")
    
    def try_direct_install(self):
        """Try to install ofScraper if not found"""
        self.update_status("Attempting to install ofScraper using pip...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "ofscraper"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                self.update_status("Successfully installed ofScraper via pip.")
                return True
            else:
                self.update_status(f"Failed to install ofScraper: {result.stderr}")
                return False
        except Exception as e:
            self.update_status(f"Error installing ofScraper: {e}")
            return False
    
    def get_pip_installed_script(self):
        """Find the actual ofScraper script installed by pip"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "-f", "ofscraper"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Get the location of the package
                location = None
                for line in result.stdout.splitlines():
                    if line.startswith("Location:"):
                        location = line.split(":", 1)[1].strip()
                        break
                
                if not location:
                    return None
                
                # Look for scripts in the output
                script_lines = [line.strip() for line in result.stdout.splitlines() 
                               if "bin/ofscraper" in line or "Scripts\\ofscraper" in line]
                
                if script_lines:
                    # Found a script reference
                    script_rel_path = script_lines[0].strip()
                    
                    # Handle relative vs absolute paths
                    if os.path.isabs(script_rel_path):
                        return script_rel_path
                    
                    # Try different approaches to construct the path
                    paths_to_try = [
                        # Direct relative to location
                        os.path.join(location, script_rel_path),
                        # Up two directories (site-packages -> Lib -> Scripts)
                        os.path.normpath(os.path.join(location, "..", "..", script_rel_path)),
                        # Up one directory if in a namespace package
                        os.path.normpath(os.path.join(location, "..", script_rel_path))
                    ]
                    
                    for path in paths_to_try:
                        self.update_status(f"Checking path: {path}")
                        if os.path.exists(path):
                            if os.name == "nt" and not path.endswith(".exe"):
                                path += ".exe"
                            if os.path.exists(path):
                                return path
                
                # If we can't find the script directly, look in common script locations
                common_script_locations = []
                
                # Add script locations relative to sys.prefix
                if hasattr(sys, "prefix"):
                    if os.name == "nt":
                        common_script_locations.append(os.path.join(sys.prefix, "Scripts"))
                    else:
                        common_script_locations.append(os.path.join(sys.prefix, "bin"))
                
                # Add user script locations
                if os.name == "nt":
                    common_script_locations.append(os.path.join(site.USER_BASE, "Scripts"))
                else:
                    common_script_locations.append(os.path.join(site.USER_BASE, "bin"))
                
                # Check each location
                for script_dir in common_script_locations:
                    script_name = "ofscraper.exe" if os.name == "nt" else "ofscraper"
                    full_path = os.path.join(script_dir, script_name)
                    if os.path.exists(full_path):
                        return full_path
        
        except Exception as e:
            self.update_status(f"Error finding pip script: {e}")
        
        return None
    
    def get_pipx_installed_script(self):
        """Find the actual ofScraper script installed by pipx"""
        try:
            # Try common pipx binary locations first
            bin_locations = []
            
            if os.name == "nt":  # Windows
                bin_locations = [
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "pipx", "bin"),
                    os.path.expanduser("~\\.local\\bin")
                ]
            else:  # Unix-like
                bin_locations = [
                    os.path.expanduser("~/.local/bin"),
                    "/usr/local/bin"
                ]
            
            # For Windows, try to find the venv Python first to avoid wrapper issues
            if os.name == "nt":
                pipx_venv_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), 
                                            "pipx", "venvs", "ofscraper")
                if os.path.isdir(pipx_venv_path):
                    # Directly run the module with the venv Python to avoid wrapper script issues
                    python_exe = os.path.join(pipx_venv_path, "Scripts", "python.exe")
                    if os.path.exists(python_exe):
                        self.update_status(f"Found pipx venv Python: {python_exe}")
                        # Instead of trying to use the wrapper, use the venv Python directly with -m
                        return [python_exe, "-m", "ofscraper"]
            
            # If we didn't return a Python + module approach, look for direct executables
            for bin_dir in bin_locations:
                script_name = "ofscraper.exe" if os.name == "nt" else "ofscraper"
                script_path = os.path.join(bin_dir, script_name)
                if os.path.exists(script_path):
                    # On Windows, don't return .exe scripts directly - they could be wrappers
                    # that need specific Python versions
                    if os.name == "nt":
                        self.update_status(f"Found pipx script at {script_path}, but will use module approach instead")
                        # Fall through to find the proper Python + module approach
                    else:
                        self.update_status(f"Found pipx script at: {script_path}")
                        return script_path
            
            # If we couldn't find it in the common locations or need module approach,
            # check pipx json output
            try:
                result = subprocess.run(
                    ["pipx", "list", "--json"],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    import json
                    data = json.loads(result.stdout)
                    
                    if "venvs" in data and "ofscraper" in data["venvs"]:
                        venv_info = data["venvs"]["ofscraper"]
                        
                        # Best approach: use the venv Python + module
                        if "venv" in venv_info:
                            venv_path = venv_info["venv"]
                            if os.name == "nt":
                                python_path = os.path.join(venv_path, "Scripts", "python.exe")
                            else:
                                bin_dir = os.path.join(venv_path, "bin")
                                python_paths = glob.glob(os.path.join(bin_dir, "python*"))
                                python_path = python_paths[0] if python_paths else None
                                
                            if python_path and os.path.exists(python_path):
                                self.update_status(f"Using pipx venv Python: {python_path}")
                                return [python_path, "-m", "ofscraper"]
            except Exception as e:
                self.update_status(f"Error checking pipx JSON: {e}")
                
        except Exception as e:
            self.update_status(f"Error finding pipx script: {e}")
            
        return None
    
    def find_installed_ofscraper_module(self):
        """Find the ofScraper module for Python module approach"""
        try:
            # First check if ofscraper module can be imported
            result = subprocess.run(
                [sys.executable, "-c", "import ofscraper; print(ofscraper.__file__)"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and 'ofscraper' in result.stdout:
                module_file = result.stdout.strip()
                self.update_status(f"Found ofScraper module at: {module_file}")
                return [sys.executable, "-m", "ofscraper"]
        except Exception:
            pass
            
        # Look in site-packages
        for site_dir in site.getsitepackages() + [site.getusersitepackages()]:
            ofscraper_dir = os.path.join(site_dir, "ofscraper")
            if os.path.isdir(ofscraper_dir):
                self.update_status(f"Found ofScraper at: {ofscraper_dir}")
                return [sys.executable, "-m", "ofscraper"]
                
        # Check pipx venv
        if os.name == "nt":  # Windows
            pipx_venv_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "pipx", "venvs", "ofscraper")
        else:  # Unix-like
            pipx_venv_path = os.path.expanduser("~/.local/pipx/venvs/ofscraper")
            
        if os.path.isdir(pipx_venv_path):
            # Find Python in pipx venv
            if os.name == "nt":
                python_path = os.path.join(pipx_venv_path, "Scripts", "python.exe")
            else:
                python_paths = glob.glob(os.path.join(pipx_venv_path, "bin", "python*"))
                python_path = python_paths[0] if python_paths else None
                
            if python_path and os.path.exists(python_path):
                self.update_status(f"Using pipx venv Python: {python_path}")
                return [python_path, "-m", "ofscraper"]
                
        return None
    
    def launch_in_terminal(self, cmd):
        """Launch ofScraper in a new terminal window"""
        try:
            if isinstance(cmd, list):
                cmd_display = " ".join(str(c) for c in cmd)
                self.update_status(f"Launching with command: {cmd_display}")
            else:
                cmd_display = cmd
                self.update_status(f"Launching with command: {cmd_display}")
                
            if os.name == "nt":  # Windows
                # Create a batch file that runs ofscraper directly rather than trying to combine executables
                batch_path = os.path.join(tempfile.gettempdir(), "run_ofscraper.bat")
                
                with open(batch_path, "w") as f:
                    # Add commands to set environment correctly
                    f.write("@echo off\n")
                    f.write("echo Running ofScraper...\n")
                    
                    # Clear PYTHONPATH to avoid loading development versions
                    f.write("set PYTHONPATH=\n")
                    
                    # Run from user's home directory
                    f.write(f"cd /d {os.path.expanduser('~')}\n")
                    
                    # Set username environment var
                    f.write(f"set USERNAME={os.environ.get('USERNAME', '')}\n")
                    
                    # For pipx or direct executable, don't use Python to run it
                    if isinstance(cmd, str) or (isinstance(cmd, list) and cmd[0].endswith(".exe")):
                        if isinstance(cmd, list):
                            # Just use the first item if it's an executable
                            f.write(f"\"{cmd[0]}\"\n")
                        else:
                            f.write(f"\"{cmd}\"\n")
                    # For Python module approach
                    elif isinstance(cmd, list) and len(cmd) >= 2 and cmd[1] == "-m":
                        f.write(f"\"{cmd[0]}\" {' '.join(cmd[1:])}\n")
                    # Generic fallback
                    else:
                        if isinstance(cmd, list):
                            cmd_str = " ".join(f'"{c}"' if ' ' in str(c) else str(c) for c in cmd)
                            f.write(f"{cmd_str}\n")
                        else:
                            f.write(f"{cmd}\n")
                    
                    # Keep window open
                    f.write("echo.\necho Press any key to close this window...\n")
                    f.write("pause > nul\n")
                
                # Make file executable and launch
                os.chmod(batch_path, 0o755)
                os.startfile(batch_path)
                return True
                
            elif sys.platform == "darwin":  # macOS
                if isinstance(cmd, list):
                    cmd_str = " ".join(f"'{c}'" if ' ' in str(c) else str(c) for c in cmd)
                else:
                    cmd_str = cmd
                    
                # Run from home directory with clean environment
                full_cmd = f"cd {os.path.expanduser('~')} && PYTHONPATH='' {cmd_str}"
                
                apple_script = f'tell application "Terminal" to do script "{full_cmd}"'
                subprocess.run(["osascript", "-e", apple_script])
                return True
                
            elif sys.platform.startswith("linux"):  # Linux
                if isinstance(cmd, list):
                    cmd_str = " ".join(f"'{c}'" if ' ' in str(c) else str(c) for c in cmd)
                else:
                    cmd_str = cmd
                    
                # Create a command that runs from home with clean environment
                full_cmd = f"cd {os.path.expanduser('~')} && PYTHONPATH='' {cmd_str}; exec bash"
                
                if shutil.which("gnome-terminal"):
                    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', full_cmd])
                    return True
                elif shutil.which("xterm"):
                    subprocess.Popen(['xterm', '-e', full_cmd])
                    return True
                
            # No supported terminal found
            return False
            
        except Exception as e:
            self.update_status(f"Error launching terminal: {e}")
            return False
            
    def run_ofscraper_in_gui(self, ofscraper_cmd="ofscraper"):
        """Run ofscraper in a non-interactive terminal within the GUI as fallback"""
        self.update_status("Running ofScraper in embedded terminal (NON-INTERACTIVE mode)...")
        self.update_status("NOTE: This is a fallback method and doesn't allow interaction with ofScraper.")
        
        window = tk.Toplevel(self.parent)
        window.title("ofScraper Output (Non-interactive - FALLBACK MODE)")
        window.geometry("800x500")
        
        text_widget = tk.Text(window, wrap=tk.WORD, bg="black", fg="white")
        text_widget.pack(expand=True, fill="both")
        
        scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.config(yscrollcommand=scrollbar.set)
        
        def run_command():
            try:
                # Display the command being run
                if isinstance(ofscraper_cmd, list):
                    cmd_display = " ".join(ofscraper_cmd)
                    text_widget.insert(tk.END, f"Starting ofScraper with command: {cmd_display}\n\n")
                    cmd = ofscraper_cmd
                else:
                    text_widget.insert(tk.END, f"Starting ofScraper with command: {ofscraper_cmd}\n\n")
                    cmd = [ofscraper_cmd]
                
                # Set up a clean environment
                env = {}  # Start with a completely clean environment
                
                # Add only essential environment variables
                for var in ['PATH', 'SYSTEMROOT', 'USERNAME', 'USERPROFILE', 'HOMEDRIVE', 'HOMEPATH', 'TEMP', 'TMP']:
                    if var in os.environ:
                        env[var] = os.environ[var]
                
                # Ensure PYTHONIOENCODING is set
                env["PYTHONIOENCODING"] = "utf-8"
                
                # Set USERNAME explicitly to replace placeholders
                env["USERNAME"] = os.environ.get('USERNAME', os.path.basename(os.path.expanduser('~')))
                
                # Execute the command with the clean environment
                proc = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    cwd=os.path.expanduser("~")  # Run from home directory
                )
                
                # Read output
                for line in iter(proc.stdout.readline, ""):
                    text_widget.insert(tk.END, line)
                    text_widget.see(tk.END)
                    text_widget.update_idletasks()
                    
                proc.stdout.close()
                return_code = proc.wait()
                text_widget.insert(tk.END, f"\nofScraper has exited with code {return_code}.")
                
            except Exception as e:
                text_widget.insert(tk.END, f"\nError running ofScraper: {e}")
                text_widget.insert(tk.END, "\n\nTrying alternate method...")
                
                try:
                    # Fallback to direct Python module import
                    alternate_cmd = [sys.executable, "-m", "ofscraper"]
                    text_widget.insert(tk.END, f"\nTrying: {' '.join(alternate_cmd)}\n")
                    
                    alt_proc = subprocess.Popen(
                        alternate_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        env=env,
                        cwd=os.path.expanduser("~")  # Run from home directory
                    )
                    
                    for line in iter(alt_proc.stdout.readline, ""):
                        text_widget.insert(tk.END, line)
                        text_widget.see(tk.END)
                        text_widget.update_idletasks()
                        
                    alt_proc.stdout.close()
                    alt_proc.wait()
                except Exception as e2:
                    text_widget.insert(tk.END, f"\nError with alternate method: {e2}")
                
        threading.Thread(target=run_command, daemon=True).start()

# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Run Tool")
    
    def print_to_console(message):
        print(message)
        
    tool = TestRunTool(root, print_to_console)
    tool.run()
    
    root.mainloop()