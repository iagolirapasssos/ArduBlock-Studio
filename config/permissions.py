"""Platform-specific permission management."""
import json
import os
import platform
import subprocess
import shutil
from pathlib import Path
import glob

class PermissionManager:
    """Manages system permissions for serial communication."""
    
    def __init__(self):
        self.system = platform.system()
        self.config_dir = self._get_config_dir()
        self.perm_file = self.config_dir / "permissions.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_config_dir(self) -> Path:
        """Get OS-specific configuration directory."""
        if self.system == "Windows":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
            return Path(base) / "ArduBlockStudio"
        elif self.system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "ArduBlockStudio"
        else:
            return Path.home() / ".config" / "ardublock-studio"
    
    def is_configured(self) -> bool:
        """Check if permissions are already configured."""
        if not self.perm_file.exists():
            return False
        try:
            data = json.loads(self.perm_file.read_text())
            return data.get("permissions_granted") and data.get("platform") == self.system
        except (json.JSONDecodeError, KeyError):
            return False
    
    def save_status(self):
        """Save permission status to config file."""
        data = {
            "permissions_granted": True,
            "platform": self.system,
            "timestamp": str(self.perm_file.stat().st_mtime if self.perm_file.exists() else 0)
        }
        self.perm_file.write_text(json.dumps(data, indent=2))
    
    def _setup_linux_udev(self) -> bool:
        """Set up udev rules for Arduino devices on Linux."""
        udev_file = Path("/etc/udev/rules.d/99-arduino.rules")
        if udev_file.exists():
            return True
            
        udev_rules = self._get_udev_rules()
        try:
            if shutil.which('pkexec'):
                subprocess.run([
                    'pkexec', 'bash', '-c',
                    f'echo "{udev_rules}" > {udev_file} && udevadm control --reload-rules'
                ], timeout=30)
                return True
        except subprocess.SubprocessError:
            pass
        return False
    
    def _get_udev_rules(self) -> str:
        """Get udev rules for common Arduino boards."""
        return """# Arduino and compatible boards
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0001", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0010", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0036", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0058", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666"
"""
    
    def setup(self) -> bool:
        """Configure all necessary permissions."""
        if self.is_configured():
            return True
            
        permissions_ok = True
        if self.system == "Linux":
            permissions_ok = self._setup_linux_permissions()
        elif self.system == "Darwin":
            permissions_ok = self._setup_macos_permissions()
        elif self.system == "Windows":
            permissions_ok = self._setup_windows_permissions()
        
        if permissions_ok:
            self.save_status()
        return permissions_ok
    
    def _setup_linux_permissions(self) -> bool:
        """Configure Linux-specific permissions."""
        success = True
        # Check/configure dialout group
        try:
            result = subprocess.run(['groups'], capture_output=True, text=True)
            if 'dialout' not in result.stdout:
                if shutil.which('pkexec'):
                    subprocess.run(['pkexec', 'usermod', '-aG', 'dialout', os.getlogin()], timeout=30)
        except subprocess.SubprocessError:
            success = False
        
        # Set up udev rules
        if not self._setup_linux_udev():
            success = False
        
        return success
    
    def _setup_macos_permissions(self) -> bool:
        """Configure macOS-specific permissions."""
        # macOS typically doesn't need special permissions
        return True
    
    def _setup_windows_permissions(self) -> bool:
        """Configure Windows-specific permissions."""
        try:
            firewall_rule = 'ArduBlock Studio Serial'
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', f'name={firewall_rule}'],
                capture_output=True, text=True
            )
            if "Nenhuma" in result.stdout or "No rules" in result.stdout:
                subprocess.run([
                    'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                    f'name={firewall_rule}', 'dir=in', 'action=allow',
                    'program=' + sys.executable, 'enable=yes'
                ], capture_output=True)
        except subprocess.SubprocessError:
            pass
        return True
    
    def grant_port_permissions(self, port: str = None) -> bool:
        """Grant permissions for a specific serial port."""
        if not port or self.is_configured():
            return True
            
        if self.system == "Linux" and os.path.exists(port):
            try:
                import stat
                mode = os.stat(port).st_mode
                if not (mode & stat.S_IWGRP):
                    if shutil.which('pkexec'):
                        subprocess.run(['pkexec', 'chmod', '666', port], timeout=5)
                        return True
            except (subprocess.SubprocessError, OSError):
                pass
        return True