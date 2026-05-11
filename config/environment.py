"""Environment setup and dependency checking."""
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Tuple, List

class EnvironmentSetup:
    """Handles environment setup and dependency management."""
    
    @staticmethod
    def check_python_dependencies() -> Tuple[bool, List[str]]:
        """Check if required Python packages are installed."""
        required = {
            "PyQt6": "PyQt6-WebEngine",
            "serial": "pyserial",
        }
        missing = []
        
        for module, package in required.items():
            try:
                __import__(module)
            except ImportError:
                missing.append(package)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def install_dependencies(missing: List[str]) -> bool:
        """Attempt to install missing dependencies."""
        for package in missing:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"Installed: {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install: {package}")
                return False
        return True
    
    @staticmethod
    def find_arduino_cli() -> str:
        """Locate arduino-cli in system."""
        cli_path = shutil.which("arduino-cli")
        if cli_path:
            return cli_path
        
        system = platform.system()
        search_paths = []
        
        if system == "Windows":
            import os
            search_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Arduino15\arduino-cli.exe"),
                r"C:\Program Files\Arduino CLI\arduino-cli.exe",
                r"C:\Program Files (x86)\Arduino CLI\arduino-cli.exe",
            ]
        elif system == "Darwin":
            search_paths = [
                Path.home() / ".local/bin/arduino-cli",
                "/usr/local/bin/arduino-cli",
                "/opt/homebrew/bin/arduino-cli",
            ]
        else:  # Linux
            search_paths = [
                Path.home() / ".local/bin/arduino-cli",
                "/usr/local/bin/arduino-cli",
                "/usr/bin/arduino-cli",
            ]
        
        for path in search_paths:
            if Path(path).is_file():
                try:
                    Path(path).chmod(0o755)
                except (PermissionError, OSError):
                    pass
                return str(path)
        
        return None
    
    @staticmethod
    def get_platform_info() -> dict:
        """Get platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }