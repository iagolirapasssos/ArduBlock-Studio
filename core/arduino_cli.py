"""Arduino CLI interface for compilation and upload."""
import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
import glob
from pathlib import Path
from typing import Tuple, List, Dict, Optional

class ArduinoCLI:
    """Wrapper around arduino-cli for board management."""
    
    def __init__(self):
        self.cli_path = self._find_cli()
        self.sketch_dir = Path(tempfile.mkdtemp(prefix="ardublock_"))
        self.sketch_file = self.sketch_dir / "sketch" / "sketch.ino"
        self.sketch_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _find_cli(self) -> Optional[str]:
        """Locate arduino-cli executable."""
        candidates = ["arduino-cli"]
        system = platform.system()
        
        if system == "Windows":
            candidates.extend([
                os.path.expandvars(r"%LOCALAPPDATA%\Arduino15\arduino-cli.exe"),
                r"C:\Program Files\Arduino CLI\arduino-cli.exe",
            ])
        else:
            candidates.extend([
                os.path.expanduser("~/.local/bin/arduino-cli"),
                "/usr/local/bin/arduino-cli",
                "/opt/homebrew/bin/arduino-cli",
            ])
        
        for candidate in candidates:
            if shutil.which(candidate):
                return candidate
            if os.path.isfile(candidate):
                try:
                    os.chmod(candidate, 0o755)
                except OSError:
                    pass
                return candidate
        return None
    
    def is_available(self) -> bool:
        """Check if arduino-cli is available."""
        return self.cli_path is not None
    
    def run_command(self, args: List[str], timeout: int = 120) -> Tuple[bool, str]:
        """Execute an arduino-cli command."""
        if not self.cli_path:
            return False, "arduino-cli not found"
        
        cmd = [self.cli_path] + args + ["--format", "json"]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                encoding="utf-8", errors="replace"
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def detect_boards(self) -> List[Dict]:
        """Detect connected Arduino boards."""
        boards = []
        
        # Try arduino-cli first
        if self.cli_path:
            try:
                result = subprocess.run(
                    [self.cli_path, "board", "list", "--format", "json"],
                    capture_output=True, text=True, timeout=20,
                    encoding="utf-8", errors="replace"
                )
                if result.stdout.strip():
                    data = json.loads(result.stdout)
                    boards = self._parse_board_list(data)
            except (subprocess.SubprocessError, json.JSONDecodeError):
                pass
        
        # Fallback to pyserial
        if not boards:
            boards = self._detect_serial_boards()
        
        return boards
    
    def _parse_board_list(self, data) -> List[Dict]:
        """Parse board list from arduino-cli output."""
        boards = []
        items = data.get("detected_ports", []) if isinstance(data, dict) else data
        
        for item in items:
            port_info = item.get("port") or {}
            addr = port_info.get("address") or item.get("address", "")
            if not addr:
                continue
            
            matching = item.get("matching_boards") or []
            if matching:
                for mb in matching:
                    boards.append({
                        "port": addr,
                        "protocol": port_info.get("protocol", "serial"),
                        "name": mb.get("name", "Arduino"),
                        "fqbn": mb.get("fqbn", ""),
                    })
            else:
                boards.append({
                    "port": addr,
                    "protocol": port_info.get("protocol", "serial"),
                    "name": item.get("board_name", "Serial Port"),
                    "fqbn": item.get("fqbn", ""),
                })
        return boards
    
    def _detect_serial_boards(self) -> List[Dict]:
        """Detect boards using serial port scanning."""
        boards = []
        try:
            import serial.tools.list_ports as list_ports
            for port in list_ports.comports():
                boards.append({
                    "port": port.device,
                    "protocol": "serial",
                    "name": port.description or "Serial Port",
                    "fqbn": "",
                })
        except ImportError:
            pass
        return boards
    
    def compile(self, code: str, fqbn: str) -> Tuple[bool, str]:
        """Compile Arduino sketch."""
        self.sketch_file.write_text(code, encoding="utf-8")
        build_path = self.sketch_dir / "build"
        build_path.mkdir(exist_ok=True)
        
        return self.run_command(
            ["compile", "--fqbn", fqbn, "--build-path", str(build_path), str(self.sketch_file.parent)],
            timeout=120
        )
    
    def upload(self, code: str, fqbn: str, port: str) -> Tuple[bool, str]:
        """Compile and upload to board with retry logic."""
        self.sketch_file.write_text(code, encoding="utf-8")
        build_path = self.sketch_dir / "build"
        build_path.mkdir(exist_ok=True)
        
        strategies = [
            lambda: self.run_command(
                ["compile", "--upload", "--fqbn", fqbn, "-p", port,
                 "--build-path", str(build_path), str(self.sketch_file.parent)],
                timeout=200
            ),
            lambda: self._upload_hex_only(fqbn, port, build_path),
        ]
        
        for i, strategy in enumerate(strategies):
            ok, output = strategy()
            if ok:
                return True, f"Upload successful (strategy {i+1})"
        
        return False, "All upload attempts failed"
    
    def _upload_hex_only(self, fqbn: str, port: str, build_path: Path) -> Tuple[bool, str]:
        """Compile first, then upload hex file separately."""
        compile_ok, compile_out = self.compile(
            self.sketch_file.read_text(encoding="utf-8"), fqbn
        )
        if not compile_ok:
            return False, compile_out
        
        hex_files = sorted(build_path.glob("*.hex"))
        if not hex_files:
            return False, "No hex file found"
        
        return self.run_command(
            ["upload", "--fqbn", fqbn, "-p", port, "--input-file", str(hex_files[-1])],
            timeout=90
        )
    
    def get_version(self) -> str:
        """Get arduino-cli version."""
        if not self.cli_path:
            return "Not installed"
        try:
            result = subprocess.run(
                [self.cli_path, "version", "--format", "json"],
                capture_output=True, text=True, timeout=5
            )
            data = json.loads(result.stdout)
            return data.get("VersionString", "Unknown")
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return "Unknown"
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.sketch_dir, ignore_errors=True)
        except OSError:
            pass