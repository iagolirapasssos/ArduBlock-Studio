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
        # Cria um diretório temporário para o sketch
        self.sketch_dir = Path(tempfile.mkdtemp(prefix="ardublock_"))
        # O arquivo .ino deve ter o MESMO NOME do diretório pai
        # Ex: /tmp/ardublock_xxx/ardublock_xxx.ino
        self.sketch_file = self.sketch_dir / f"{self.sketch_dir.name}.ino"
        self._installed_cores = set()
        self._current_programmer = ""  # Programmer currently selected
        
        print(f"[CLI] Sketch dir: {self.sketch_dir}")
        print(f"[CLI] Sketch file: {self.sketch_file}")

    def _find_cli(self) -> Optional[str]:
        """Locate arduino-cli executable."""
        # Lista expandida de possíveis localizações
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
        
        # Busca mais profunda no home
        home = os.path.expanduser("~")
        for root, dirs, files in os.walk(home):
            if 'arduino-cli' in files:
                full_path = os.path.join(root, 'arduino-cli')
                try:
                    os.chmod(full_path, 0o755)
                except OSError:
                    pass
                return full_path
            # Limita profundidade da busca
            if root.count(os.sep) - home.count(os.sep) > 4:
                break
        
        return None
    
    def is_available(self) -> bool:
        """Check if arduino-cli is available."""
        if self.cli_path and os.path.isfile(self.cli_path):
            return True
        # Tenta encontrar novamente
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
        
        # Lista cores instalados
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
        
        # Se não encontrou, instala o core
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
                # Aumentado timeout para 30 segundos
                result = subprocess.run(
                    [self.cli_path, "board", "list", "--format", "json"],
                    capture_output=True, text=True, timeout=30,
                    encoding="utf-8", errors="replace"
                )
                if result.stdout.strip():
                    data = json.loads(result.stdout)
                    boards = self._parse_board_list(data)
                else:
                    print("[CLI] No output from board list command")
            except subprocess.TimeoutExpired:
                print("[CLI] Board detection timed out - check USB connection")
            except (subprocess.SubprocessError, json.JSONDecodeError) as e:
                print(f"[CLI] Board detection error: {e}")
        
        # SEMPRE tenta fallback com pyserial
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
                # Tenta identificar pela descrição
                desc = port_info.get("label", item.get("label", "Serial Port"))
                boards.append({
                    "port": addr,
                    "protocol": port_info.get("protocol", "serial"),
                    "name": desc or "Serial Port",
                    "fqbn": "",
                })
        return boards
    
    def _detect_serial_boards(self) -> List[Dict]:
        """Fallback: Detect boards using serial port scanning."""
        boards = []
        try:
            import serial.tools.list_ports as list_ports
            ports = list(list_ports.comports())
            print(f"[CLI] Found {len(ports)} serial port(s) via pyserial")
            
            for port in ports:
                # Tenta identificar Arduino pela descrição
                desc = port.description or ""
                name = "Serial Port"
                
                if "arduino" in desc.lower():
                    name = "Arduino (detected)"
                elif "ch340" in desc.lower() or "ch341" in desc.lower():
                    name = "Arduino Compatible (CH340)"
                elif "cp210" in desc.lower():
                    name = "Arduino Compatible (CP210x)"
                elif "ftdi" in desc.lower():
                    name = "Arduino Compatible (FTDI)"
                elif "usb serial" in desc.lower():
                    name = "USB Serial Device"
                
                boards.append({
                    "port": port.device,
                    "protocol": "serial",
                    "name": name,
                    "fqbn": "",
                })
                
            if not boards:
                print("[CLI] No serial ports found. Check:")
                print("  1. USB cable connected?")
                print("  2. Arduino powered on?")
                print("  3. Correct USB port?")
                print("  4. User in dialout group? (Linux)")
                
        except ImportError:
            print("[CLI] pyserial not available for port scanning")
            # Tenta listar dispositivos manualmente no Linux
            if platform.system() == "Linux":
                try:
                    result = subprocess.run(
                        ["ls", "-la", "/dev/ttyACM*", "/dev/ttyUSB*"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.stdout.strip():
                        print(f"[CLI] Found devices:\n{result.stdout}")
                        for line in result.stdout.strip().split('\n'):
                            if 'tty' in line:
                                parts = line.split()
                                if len(parts) >= 9:
                                    dev = "/dev/" + parts[-1]
                                    boards.append({
                                        "port": dev,
                                        "protocol": "serial",
                                        "name": f"Serial Device ({dev})",
                                        "fqbn": "",
                                    })
                except:
                    pass
                    
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
        
        # Escreve o código no arquivo .ino (com o mesmo nome do diretório)
        self.sketch_file.write_text(code, encoding="utf-8")
        
        # Cria o diretório de build
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
        
        # Constroi o comando de upload
        upload_cmd = ["upload", "--fqbn", fqbn, "-p", port]
        
        # Adiciona programador se especificado
        if programmer:
            upload_cmd.extend(["--programmer", programmer])
            print(f"[UPLOAD] Using programmer: {programmer}")
        
        print(f"[UPLOAD] Uploading to {port}...")
        print(f"[UPLOAD] Build path: {build_path}")
        
        # Primeira tentativa: upload com --input-dir
        ok, msg = self.run_command(
            upload_cmd + ["--input-dir", str(build_path)],
            timeout=120
        )
        
        if ok:
            return True, f"Upload successful{' with ' + programmer if programmer else ''}"
        
        # Segunda tentativa: upload com --input-file
        hex_files = list(build_path.glob("*.hex")) + list(build_path.glob("*.bin"))
        if hex_files:
            print(f"[UPLOAD] Trying with hex file: {hex_files[0].name}")
            ok, msg = self.run_command(
                upload_cmd + ["--input-file", str(hex_files[0])],
                timeout=120
            )
            if ok:
                return True, f"Upload successful (hex file){' with ' + programmer if programmer else ''}"
        
        # Se falhou com programador, tenta sem programador
        if programmer:
            print(f"[UPLOAD] Failed with programmer {programmer}, trying default method...")
            ok, msg = self.run_command(
                ["upload", "--fqbn", fqbn, "-p", port, "--input-dir", str(build_path)],
                timeout=120
            )
            if ok:
                return True, "Upload successful (default method - programmer failed)"
        
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