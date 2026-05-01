"""Arduino Library Manager for ArduBlock Studio."""
import json
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class LibraryInfo:
    """Information about an Arduino library."""
    name: str
    version: str = "unknown"
    author: str = "unknown"
    description: str = ""
    installed: bool = False
    install_path: str = ""


class LibraryManager:
    """Manages Arduino libraries installation and discovery."""
    
    def __init__(self, cli_path: str):
        self.cli_path = cli_path
        self.config_file = self._get_config_path()
        self.installed_libraries: Dict[str, LibraryInfo] = {}
        self._load_installed()
    
    def _get_config_path(self) -> Path:
        """Get path to library configuration file."""
        from config.permissions import PermissionManager
        pm = PermissionManager()
        return pm.config_dir / "libraries.json"
    
    def _load_installed(self):
        """Load installed libraries from config file."""
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text())
                for lib_data in data.get("libraries", []):
                    lib = LibraryInfo(**lib_data)
                    self.installed_libraries[lib.name] = lib
            except (json.JSONDecodeError, TypeError):
                pass
    
    def _save_installed(self):
        """Save installed libraries to config file."""
        data = {
            "libraries": [
                {
                    "name": lib.name,
                    "version": lib.version,
                    "author": lib.author,
                    "description": lib.description,
                    "installed": lib.installed,
                    "install_path": lib.install_path
                }
                for lib in self.installed_libraries.values()
            ]
        }
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(data, indent=2))
    
    def search_libraries(self, query: str = "") -> List[Dict]:
        """Search for available Arduino libraries.
        
        Returns list of libraries matching the query.
        """
        if not self.cli_path:
            return []
        
        try:
            cmd = [self.cli_path, "lib", "search", "--format", "json"]
            if query:
                cmd.append(query)
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace"
            )
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                libraries = data.get("libraries", []) if isinstance(data, dict) else data
                
                return [
                    {
                        "name": lib.get("name", "Unknown"),
                        "latest_version": lib.get("latest", {}).get("version", "unknown"),
                        "author": lib.get("latest", {}).get("author", "unknown"),
                        "description": lib.get("latest", {}).get("sentence", ""),
                        "installed": lib.get("name", "") in self.installed_libraries
                    }
                    for lib in libraries
                ]
        except (subprocess.SubprocessError, json.JSONDecodeError):
            pass
        
        return []
    
    def get_popular_libraries(self) -> List[Dict]:
        """Get list of commonly used Arduino libraries."""
        popular = [
            {"name": "Servo", "description": "Control servo motors"},
            {"name": "DHT sensor library", "description": "DHT11/DHT22 temperature and humidity sensor"},
            {"name": "Adafruit NeoPixel", "description": "NeoPixel LED strip control"},
            {"name": "LiquidCrystal", "description": "LCD display control"},
            {"name": "WiFi", "description": "WiFi networking (ESP8266/ESP32)"},
            {"name": "PubSubClient", "description": "MQTT client for IoT"},
            {"name": "ArduinoJson", "description": "JSON parsing and generation"},
            {"name": "Adafruit GFX Library", "description": "Graphics library for displays"},
            {"name": "Adafruit SSD1306", "description": "OLED display driver"},
            {"name": "OneWire", "description": "OneWire protocol devices"},
            {"name": "DallasTemperature", "description": "DS18B20 temperature sensor"},
            {"name": "IRremote", "description": "Infrared remote control"},
            {"name": "Adafruit Sensor", "description": "Unified sensor library"},
            {"name": "Blynk", "description": "IoT platform library"},
            {"name": "FastLED", "description": "Advanced LED strip control"},
        ]
        
        # Check which ones are installed
        for lib in popular:
            lib["installed"] = lib["name"] in self.installed_libraries
        
        return popular
    
    def install_library(self, library_name: str) -> Tuple[bool, str]:
        """Install an Arduino library by name.
        
        Returns (success, message).
        """
        if not self.cli_path:
            return False, "arduino-cli not found"
        
        try:
            result = subprocess.run(
                [self.cli_path, "lib", "install", library_name],
                capture_output=True, text=True, timeout=60,
                encoding="utf-8", errors="replace"
            )
            
            if result.returncode == 0:
                # Find where it was installed
                install_path = self._find_library_path(library_name)
                
                self.installed_libraries[library_name] = LibraryInfo(
                    name=library_name,
                    version="latest",
                    installed=True,
                    install_path=install_path or ""
                )
                self._save_installed()
                return True, f"Library '{library_name}' installed successfully"
            else:
                return False, result.stderr or "Installation failed"
                
        except subprocess.SubprocessError as e:
            return False, str(e)
    
    def _find_library_path(self, library_name: str) -> Optional[str]:
        """Find the installation path of a library."""
        # Common Arduino library paths
        search_paths = [
            Path.home() / "Arduino" / "libraries",
            Path.home() / "Documents" / "Arduino" / "libraries",
            Path("/usr/share/arduino/libraries"),
            Path("/usr/local/share/arduino/libraries"),
        ]
        
        for base_path in search_paths:
            if base_path.exists():
                for lib_dir in base_path.iterdir():
                    if lib_dir.is_dir() and library_name.lower() in lib_dir.name.lower():
                        return str(lib_dir)
        
        return None
    
    def uninstall_library(self, library_name: str) -> Tuple[bool, str]:
        """Uninstall an Arduino library.
        
        Returns (success, message).
        """
        if not self.cli_path:
            return False, "arduino-cli not found"
        
        try:
            result = subprocess.run(
                [self.cli_path, "lib", "uninstall", library_name],
                capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace"
            )
            
            if result.returncode == 0:
                if library_name in self.installed_libraries:
                    del self.installed_libraries[library_name]
                    self._save_installed()
                return True, f"Library '{library_name}' uninstalled"
            else:
                return False, result.stderr or "Uninstall failed"
                
        except subprocess.SubprocessError as e:
            return False, str(e)
    
    def get_installed_libraries(self) -> List[Dict]:
        """Get list of installed libraries."""
        return [
            {
                "name": lib.name,
                "version": lib.version,
                "author": lib.author,
                "install_path": lib.install_path
            }
            for lib in self.installed_libraries.values()
            if lib.installed
        ]
    
    def install_from_zip(self, zip_path: str) -> Tuple[bool, str]:
        """Install a library from a ZIP file.
        
        Returns (success, message).
        """
        if not self.cli_path:
            return False, "arduino-cli not found"
        
        try:
            result = subprocess.run(
                [self.cli_path, "lib", "install", "--zip-path", zip_path],
                capture_output=True, text=True, timeout=60,
                encoding="utf-8", errors="replace"
            )
            
            if result.returncode == 0:
                return True, "Library installed from ZIP successfully"
            else:
                return False, result.stderr or "ZIP installation failed"
                
        except subprocess.SubprocessError as e:
            return False, str(e)