"""Arduino CLI interface for compilation and upload with programmer support."""
import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Tuple, List, Dict, Optional


class ArduinoCLI:
    """Wrapper around arduino-cli for board management and programming."""
    
    # Lista de programadores suportados
    SUPPORTED_PROGRAMMERS = [
        {"id": "", "name": "Default (No Programmer)", "protocol": ""},
        {"id": "avrispmkii", "name": "AVR ISP mkII", "protocol": "stk500v2"},
        {"id": "avrisp", "name": "AVR ISP", "protocol": "stk500v1"},
        {"id": "usbasp", "name": "USBasp", "protocol": "usbasp"},
        {"id": "usbtinyisp", "name": "USBtinyISP", "protocol": "usbtiny"},
        {"id": "arduinoisp", "name": "Arduino as ISP", "protocol": "stk500v1"},
        {"id": "arduinoasisp", "name": "Arduino as ISP (ATmega32U4)", "protocol": "avr109"},
        {"id": "atmel_ice", "name": "Atmel-ICE (AVR)", "protocol": "jtag"},
        {"id": "pickit4", "name": "PICkit 4 / Snap", "protocol": "pic32prog"},
        {"id": "jlink", "name": "Segger J-Link", "protocol": "jlink"},
        {"id": "stlink", "name": "ST-Link", "protocol": "stlink"},
    ]
    
    def __init__(self):
        self.cli_path = self._find_cli()
        self.sketch_dir = Path(tempfile.mkdtemp(prefix="ardublock_"))
        self.sketch_file = self.sketch_dir / f"{self.sketch_dir.name}.ino"
        self._installed_cores = set()
        self._current_programmer = ""
        
        print(f"[CLI] Sketch dir: {self.sketch_dir}")
        print(f"[CLI] Sketch file: {self.sketch_file}")

    def _find_cli(self) -> Optional[str]:
        """Locate arduino-cli executable."""
        candidates = [
            "arduino-cli",
            os.path.expanduser("~/bin/arduino-cli"),
            os.path.expanduser("~/.local/bin/arduino-cli"),
            "/usr/local/bin/arduino-cli",
            "/usr/bin/arduino-cli",
            "/opt/homebrew/bin/arduino-cli",
        ]
        
        system = platform.system()
        if system == "Windows":
            candidates.extend([
                os.path.expandvars(r"%LOCALAPPDATA%\Arduino15\arduino-cli.exe"),
                r"C:\Program Files\Arduino CLI\arduino-cli.exe",
            ])
        
        for candidate in candidates:
            if shutil.which(candidate):
                return shutil.which(candidate)
            if os.path.isfile(candidate):
                try:
                    os.chmod(candidate, 0o755)
                except OSError:
                    pass
                return candidate
        
        home = os.path.expanduser("~")
        for root, dirs, files in os.walk(home):
            if 'arduino-cli' in files or 'arduino-cli.exe' in files:
                full_path = os.path.join(root, 'arduino-cli')
                if not os.path.exists(full_path):
                    full_path = os.path.join(root, 'arduino-cli.exe')
                try:
                    os.chmod(full_path, 0o755)
                except OSError:
                    pass
                return full_path
            if root.count(os.sep) - home.count(os.sep) > 4:
                break
        
        return None
    
    def is_available(self) -> bool:
        """Check if arduino-cli is available."""
        if self.cli_path and os.path.isfile(self.cli_path):
            return True
        self.cli_path = self._find_cli()
        return self.cli_path is not None
    
    def run_command(self, args: List[str], timeout: int = 120) -> Tuple[bool, str]:
        """Execute an arduino-cli command with better error handling."""
        if not self.cli_path:
            return False, "arduino-cli not found"
        
        cmd = [self.cli_path] + args
        print(f"[CLI] Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                encoding="utf-8", 
                errors="replace"
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                print(f"[CLI] Command failed (code {result.returncode}): {error_msg[:200]}")
                return False, error_msg
            
            return True, result.stdout
            
        except subprocess.TimeoutExpired:
            print(f"[CLI] Command timed out after {timeout}s: {' '.join(cmd)}")
            return False, f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return False, f"arduino-cli not found at {self.cli_path}"
        except Exception as e:
            return False, str(e)
    
    def ensure_core_installed(self, fqbn: str) -> Tuple[bool, str]:
        """Ensure the core for the board is installed."""
        parts = fqbn.split(":")
        if len(parts) >= 2:
            core = f"{parts[0]}:{parts[1]}"
        else:
            core = fqbn
        
        if core in self._installed_cores:
            return True, "Core already installed"
        
        print(f"[CLI] Checking core: {core}")
        
        ok, output = self.run_command(["core", "list", "--format", "json"], timeout=30)
        if ok and output.strip():
            try:
                cores_data = json.loads(output)
                if isinstance(cores_data, list):
                    for c in cores_data:
                        if isinstance(c, dict) and c.get("id", "").startswith(core):
                            self._installed_cores.add(core)
                            return True, f"Core {core} already installed"
            except json.JSONDecodeError as e:
                print(f"[CLI] JSON decode error: {e}")
        
        print(f"[CLI] Installing core: {core}")
        ok, output = self.run_command(["core", "install", core], timeout=300)
        if ok:
            self._installed_cores.add(core)
            return True, f"Core {core} installed successfully"
        else:
            return False, f"Failed to install core {core}: {output}"
    
    def detect_boards(self) -> List[Dict]:
        """Detect connected Arduino boards."""
        boards = []
        
        if self.cli_path:
            try:
                timeout = 10 if platform.system() == "Windows" else 20
                
                result = subprocess.run(
                    [self.cli_path, "board", "list", "--format", "json"],
                    capture_output=True, text=True, timeout=timeout,
                    encoding="utf-8", errors="replace"
                )
                if result.stdout.strip():
                    data = json.loads(result.stdout)
                    boards = self._parse_board_list(data)
                else:
                    print("[CLI] No output from board list command")
                    
            except subprocess.TimeoutExpired:
                print(f"[CLI] Board detection timed out after {timeout}s")
            except (subprocess.SubprocessError, json.JSONDecodeError) as e:
                print(f"[CLI] Board detection error: {e}")
        
        if not boards:
            boards = self._detect_serial_boards()
            
        return boards
    
    def _parse_board_list(self, data) -> List[Dict]:
        """Parse board list from modern arduino-cli JSON output."""
        boards = []
        items = data if isinstance(data, list) else data.get("detected_ports", [])
        
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
                desc = port_info.get("label", item.get("label", "Serial Port"))
                boards.append({
                    "port": addr,
                    "protocol": port_info.get("protocol", "serial"),
                    "name": desc or "Serial Port",
                    "fqbn": "",
                })
        return boards
    
    def _detect_serial_boards(self) -> List[Dict]:
        """Fallback: Detect boards using serial port scanning.
        Works on Windows, Linux, and macOS.
        """
        boards = []
        current_os = platform.system()
        
        # ================================================================
        # MÉTODO 1: pyserial (funciona em todos os sistemas)
        # ================================================================
        try:
            import serial.tools.list_ports as list_ports
            ports = list(list_ports.comports())
            print(f"[CLI] pyserial found {len(ports)} port(s)")
            
            for port in ports:
                desc = port.description or ""
                hwid = port.hwid or ""
                device_name = desc or f"Serial Port ({port.device})"
                
                # Identificar Arduino
                lower_desc = desc.lower()
                lower_hwid = hwid.lower()
                
                if "arduino" in lower_desc or "arduino" in lower_hwid:
                    device_name = f"Arduino - {desc}"
                elif "ch340" in lower_desc or "ch340" in lower_hwid:
                    device_name = f"Arduino Clone (CH340) - {desc}"
                elif "ch341" in lower_desc or "ch341" in lower_hwid:
                    device_name = f"Arduino Clone (CH341) - {desc}"
                elif "cp210" in lower_desc or "cp210" in lower_hwid:
                    device_name = f"Arduino Compatible (CP210x) - {desc}"
                elif "ftdi" in lower_desc or "ftdi" in lower_hwid:
                    device_name = f"Arduino Compatible (FTDI) - {desc}"
                elif "usb serial" in lower_desc or "usb-serial" in lower_desc:
                    device_name = f"USB Serial - {desc}"
                
                boards.append({
                    "port": port.device,
                    "protocol": "serial",
                    "name": device_name,
                    "fqbn": "",
                    "vid_pid": f"VID:{port.vid:04X}/PID:{port.pid:04X}" if port.vid and port.pid else "",
                    "manufacturer": port.manufacturer or "",
                    "serial_number": port.serial_number or "",
                })
            
            if boards:
                return boards
                
        except ImportError:
            print("[CLI] pyserial not installed. Install with: pip install pyserial")
        except Exception as e:
            print(f"[CLI] pyserial error: {e}")
        
        # ================================================================
        # MÉTODO 2: Windows - PowerShell (mais confiável)
        # ================================================================
        if current_os == "Windows":
            boards = self._detect_windows_ports_powershell()
            if boards:
                return boards
            
            # Fallback: Registro do Windows
            boards = self._detect_windows_ports_registry()
            if boards:
                return boards
        
        # ================================================================
        # MÉTODO 3: Linux - /dev/tty* devices
        # ================================================================
        elif current_os == "Linux":
            try:
                import glob
                for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*']:
                    for device in glob.glob(pattern):
                        boards.append({
                            "port": device,
                            "protocol": "serial",
                            "name": os.path.basename(device),
                            "fqbn": "",
                        })
                if boards:
                    print(f"[CLI] Found {len(boards)} device(s) via /dev scan")
            except Exception as e:
                print(f"[CLI] Linux scan error: {e}")
        
        # ================================================================
        # MÉTODO 4: macOS - /dev/cu.* and /dev/tty.* devices
        # ================================================================
        elif current_os == "Darwin":
            try:
                import glob
                for pattern in ['/dev/cu.usb*', '/dev/cu.wchusbserial*']:
                    for device in glob.glob(pattern):
                        boards.append({
                            "port": device,
                            "protocol": "serial",
                            "name": os.path.basename(device),
                            "fqbn": "",
                        })
                if boards:
                    print(f"[CLI] Found {len(boards)} device(s) via macOS scan")
            except Exception as e:
                print(f"[CLI] macOS scan error: {e}")
        
        # ================================================================
        # DIAGNÓSTICO FINAL
        # ================================================================
        if not boards:
            print("[CLI] ⚠️ No serial ports detected!")
            print("[CLI] Troubleshooting:")
            if current_os == "Windows":
                print("  1. Check Device Manager > Ports (COM & LPT)")
                print("  2. Install CH340/CP210x drivers: https://sparks.gogo.co.nz/ch340.html")
                print("  3. Try a different USB cable (must be DATA cable, not charge-only)")
                print("  4. Try a different USB port (USB 2.0 preferred)")
                print("  5. Test with Arduino IDE first to verify board works")
            elif current_os == "Linux":
                print("  1. Run: ls -la /dev/ttyUSB* /dev/ttyACM*")
                print("  2. Run: sudo usermod -aG dialout $USER && logout/login")
            elif current_os == "Darwin":
                print("  1. Run: ls -la /dev/cu.* /dev/tty.*")
                print("  2. Install CH340/CP210x drivers for macOS")
        
        return boards

    def _detect_windows_ports_powershell(self) -> List[Dict]:
        """Detect COM ports using PowerShell."""
        boards = []
        try:
            # PowerShell com timeout
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 '[System.IO.Ports.SerialPort]::GetPortNames() | ForEach-Object { $_ }'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for port in result.stdout.strip().split('\n'):
                    port = port.strip()
                    if port and port not in [b['port'] for b in boards]:
                        boards.append({
                            "port": port,
                            "protocol": "serial",
                            "name": f"COM Port ({port})",
                            "fqbn": "",
                        })
                print(f"[CLI] Found {len(boards)} port(s) via PowerShell")
                
        except subprocess.TimeoutExpired:
            print("[CLI] PowerShell timed out")
        except FileNotFoundError:
            print("[CLI] PowerShell not available")
        except Exception as e:
            print(f"[CLI] PowerShell error: {e}")
        
        return boards

    def _detect_windows_ports_registry(self) -> List[Dict]:
        """Detect COM ports from Windows Registry."""
        boards = []
        try:
            import winreg
            
            key_path = "HARDWARE\\DEVICEMAP\\SERIALCOMM"
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if value not in [b['port'] for b in boards]:
                            boards.append({
                                "port": value,
                                "protocol": "serial",
                                "name": f"{name} ({value})",
                                "fqbn": "",
                            })
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(key)
                
                if boards:
                    print(f"[CLI] Found {len(boards)} port(s) via Registry")
                    
            except WindowsError:
                pass
                
        except ImportError:
            print("[CLI] winreg not available")
        except Exception as e:
            print(f"[CLI] Registry error: {e}")
        
        return boards
    
    def set_programmer(self, programmer_id: str):
        """Set the programmer to use for upload."""
        self._current_programmer = programmer_id
        print(f"[CLI] Programmer set to: {programmer_id or 'None (default)'}")
    
    def get_programmers(self) -> List[Dict]:
        """Get list of supported programmers."""
        return self.SUPPORTED_PROGRAMMERS.copy()
    
    def compile(self, code: str, fqbn: str) -> Tuple[bool, str]:
        """Compile Arduino sketch."""
        ok, msg = self.ensure_core_installed(fqbn)
        if not ok:
            return False, msg
        
        self.sketch_file.write_text(code, encoding="utf-8")
        
        build_path = self.sketch_dir / "build"
        build_path.mkdir(exist_ok=True)
        
        print(f"[CLI] Compiling for {fqbn}...")
        print(f"[CLI] Sketch dir: {self.sketch_dir}")
        print(f"[CLI] Sketch file: {self.sketch_file}")
        print(f"[CLI] Build path: {build_path}")
        
        return self.run_command(
            ["compile", "--fqbn", fqbn, "--build-path", str(build_path), str(self.sketch_dir)],
            timeout=180
        )
    
    def upload(self, code: str, fqbn: str, port: str, programmer: str = "") -> Tuple[bool, str]:
        """Upload Arduino sketch using specified programmer."""
        print("[UPLOAD] Compiling sketch before upload...")
        ok, msg = self.compile(code, fqbn)
        if not ok:
            return False, f"Compilation failed:\n{msg}"
        
        build_path = self.sketch_dir / "build"
        upload_cmd = ["upload", "--fqbn", fqbn, "-p", port]
        
        if programmer:
            upload_cmd.extend(["--programmer", programmer])
            print(f"[UPLOAD] Using programmer: {programmer}")
        
        print(f"[UPLOAD] Uploading to {port}...")
        
        # Tentativa 1: --input-dir
        ok, msg = self.run_command(
            upload_cmd + ["--input-dir", str(build_path)],
            timeout=120
        )
        
        if ok:
            return True, f"Upload successful{' with ' + programmer if programmer else ''}"
        
        # Tentativa 2: --input-file
        hex_files = list(build_path.glob("*.hex")) + list(build_path.glob("*.bin"))
        if hex_files:
            print(f"[UPLOAD] Trying with hex file: {hex_files[0].name}")
            ok, msg = self.run_command(
                upload_cmd + ["--input-file", str(hex_files[0])],
                timeout=120
            )
            if ok:
                return True, f"Upload successful (hex file)"
        
        # Tentativa 3: sem programador
        if programmer:
            print(f"[UPLOAD] Failed with programmer, trying default method...")
            ok, msg = self.run_command(
                ["upload", "--fqbn", fqbn, "-p", port, "--input-dir", str(build_path)],
                timeout=120
            )
            if ok:
                return True, "Upload successful (default method)"
        
        return False, f"Upload failed:\n{msg}"
    
    def get_version(self) -> str:
        """Get arduino-cli version."""
        if not self.cli_path:
            return "Not installed"
        try:
            result = subprocess.run(
                [self.cli_path, "version", "--format", "json"],
                capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace"
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                return data.get("VersionString", data.get("Application", "Unknown"))
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"[CLI] Version check error: {e}")
        return "Unknown"
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.sketch_dir, ignore_errors=True)
        except OSError:
            pass