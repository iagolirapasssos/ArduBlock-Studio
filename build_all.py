#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empacotador Universal do ArduBlock Studio v3.6
COM GERENCIAMENTO DE PROCESSOS WINE E TIMEOUTS
"""

import os
import sys
import platform
import subprocess
import shutil
import json
import zipfile
import tarfile
import hashlib
import time
import glob
import signal
from pathlib import Path
from datetime import datetime

class UniversalPackager:
    def __init__(self, wine_python_path=None):
        self.project_root = Path(__file__).parent.resolve()
        self.build_dir = self.project_root / "dist"
        self.cache_dir = self.build_dir / ".cache"
        # CORRIGIDO: Arquivo principal é main.py
        self.source_file = self.project_root / "main.py"
        self.current_os = platform.system()
        self.version = "3.6.0"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wine_python_path = wine_python_path
        
        if not self.source_file.exists():
            print(f"❌ ERRO: {self.source_file} nao encontrado!")
            sys.exit(1)
        
        self.source_hash = hashlib.md5(self.source_file.read_bytes()).hexdigest()[:12]
        
        self.platform_configs = {
            "Windows": {
                "name": "ArduBlockStudio", "ext": ".exe", "icon": "🪟",
                "hidden_imports": [
                    "PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", 
                    "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel",
                    "serial", "json", "tempfile", "shutil", "threading",
                    "subprocess", "glob", "pathlib", "platform",
                    # Importante: incluir módulos do projeto
                    "config", "config.permissions", "config.environment",
                    "core", "core.arduino_cli", "core.boards", "core.library_manager",
                    "core.compilation_cache", "core.project_history", 
                    "core.error_handler", "core.pdf_exporter",
                    "ui", "ui.bridge", "ui.main_window", "ui.serial_monitor",
                    "ui.library_dialog",
                    "resources", "resources.blockly_html",
                    "i18n", "i18n.translations", "i18n.en", "i18n.pt",
                    "extensions", "extensions.manager", "extensions.api",
                    "extensions.repository",
                ],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            },
            "Darwin": {
                "name": "ArduBlockStudio", "ext": ".app", "icon": "🍎",
                "hidden_imports": [
                    "PyQt6", "PyQt6.QtCore", "PyQt6.QtGui",
                    "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel",
                    "serial", "json", "tempfile", "shutil", "threading",
                    "subprocess", "glob", "pathlib", "platform",
                    "config", "config.permissions", "config.environment",
                    "core", "core.arduino_cli", "core.boards", "core.library_manager",
                    "ui", "ui.bridge", "ui.main_window", "ui.serial_monitor",
                    "resources", "resources.blockly_html",
                    "i18n", "i18n.translations", "i18n.en", "i18n.pt",
                    "extensions", "extensions.manager", "extensions.api",
                ],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            },
            "Linux": {
                "name": "ardublock-studio", "ext": "", "icon": "🐧",
                "hidden_imports": [
                    "PyQt6", "PyQt6.QtCore", "PyQt6.QtGui",
                    "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel",
                    "serial", "json", "tempfile", "shutil", "threading",
                    "subprocess", "glob", "pathlib", "platform",
                    "config", "config.permissions", "config.environment",
                    "core", "core.arduino_cli", "core.boards", "core.library_manager",
                    "core.compilation_cache", "core.project_history",
                    "core.error_handler", "core.pdf_exporter",
                    "ui", "ui.bridge", "ui.main_window", "ui.serial_monitor",
                    "ui.library_dialog",
                    "resources", "resources.blockly_html",
                    "i18n", "i18n.translations", "i18n.en", "i18n.pt",
                    "extensions", "extensions.manager", "extensions.api",
                    "extensions.repository",
                    "extensions.advanced_math", "extensions.advanced_logic",
                    "extensions.advanced_pins",
                ],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            }
        }
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        for plat in ["windows", "macos", "linux"]:
            (self.build_dir / plat).mkdir(exist_ok=True)
        
        self.cache = self._load_cache()

    def _load_cache(self):
        cache_file = self.cache_dir / "build_cache.json"
        if cache_file.exists():
            try:
                return json.loads(cache_file.read_text())
            except:
                pass
        return {}

    def _save_cache(self):
        (self.cache_dir / "build_cache.json").write_text(json.dumps(self.cache, indent=2))

    def _run_cmd(self, cmd, timeout=600):
        """Executa comando e retorna (success, stdout, stderr)."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Timeout after {timeout}s"
        except Exception as e:
            return False, "", str(e)

    def _kill_wine_processes(self):
        """Mata todos os processos Wine pendentes"""
        try:
            subprocess.run(["wineserver", "-k"], capture_output=True, timeout=10)
            time.sleep(2)
            print("   🍷 Processos Wine limpos")
        except:
            pass

    def _should_skip(self, platform_name):
        config = self.platform_configs[platform_name]
        output_dir = self.build_dir / platform_name.lower()
        
        if platform_name == "Darwin":
            apps = list(output_dir.glob("*.app"))
            if not apps:
                return False
            path = str(apps[0])
        else:
            exe_path = output_dir / (config["name"] + config["ext"])
            if not exe_path.exists() or exe_path.stat().st_size < 1000000:
                return False
            path = str(exe_path)
        
        cache_key = platform_name + "_" + self.source_hash
        if cache_key in self.cache and self.cache[cache_key].get("path") == path:
            size_mb = Path(path).stat().st_size / (1024*1024)
            print(f"   {config['icon']} ♻️  Ja existe: {Path(path).name} ({size_mb:.1f} MB)")
            return True
        return False

    def check_dependencies(self):
        print("=" * 60)
        print("🔍 DEPENDENCIAS")
        print("=" * 60)
        
        try:
            import PyInstaller
            print("   ✅ PyInstaller")
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("   ✅ PyInstaller instalado")
        
        wine_ok = False
        if self.current_os != "Windows":
            if shutil.which("wine") or shutil.which("wine64"):
                print("   ✅ Wine")
                wine_ok = True
            else:
                print("   ⚠️ Wine nao instalado")
        
        docker_ok = shutil.which("docker") is not None
        if docker_ok:
            print("   ✅ Docker")
        
        wsl_ok = self.current_os == "Windows" and shutil.which("wsl") is not None
        print()
        return wine_ok, docker_ok, wsl_ok

    def build_linux(self, force=False, wine_ok=False, docker_ok=False, wsl_ok=False):
        icon = "🐧"
        print("\n" + "=" * 60)
        print(f"{icon} LINUX")
        print("=" * 60)
        
        if not force and self._should_skip("Linux"):
            return True
        
        output_dir = self.build_dir / "linux"
        
        if self.current_os == "Linux":
            return self._pyinstaller_build("Linux", output_dir)
        elif self.current_os == "Windows" and wsl_ok:
            return self._build_linux_via_wsl(output_dir)
        elif docker_ok:
            return self._build_linux_via_docker(output_dir)
        return False

    def build_windows(self, force=False, wine_ok=False, docker_ok=False):
        icon = "🪟"
        print("\n" + "=" * 60)
        print(f"{icon} WINDOWS")
        print("=" * 60)
        
        if not force and self._should_skip("Windows"):
            return True
        
        if self.current_os == "Windows":
            return self._pyinstaller_build("Windows", self.build_dir / "windows")
        elif wine_ok:
            return self._build_windows_via_wine()
        else:
            print(f"   {icon} ⚠️ Wine necessario")
            self._create_windows_build_script()
            return False

    def build_macos(self, force=False, docker_ok=False):
        icon = "🍎"
        print("\n" + "=" * 60)
        print(f"{icon} macOS")
        print("=" * 60)
        
        if not force and self._should_skip("macOS"):
            return True
        
        if self.current_os == "Darwin":
            return self._pyinstaller_build("Darwin", self.build_dir / "macos")
        else:
            print(f"   {icon} ⚠️ Requer macOS")
            self._create_macos_build_script()
            return False

    def _pyinstaller_build(self, platform_name, output_dir):
        config = self.platform_configs[platform_name]
        icon = config["icon"]
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile", "--windowed", "--clean", "--noconfirm",
            "--name=" + config["name"],
            "--distpath=" + str(output_dir),
            "--workpath=" + str(self.build_dir / "build" / platform_name.lower()),
            "--specpath=" + str(self.build_dir / "specs"),
        ]
        
        # ADICIONAR ARQUIVOS DE DADOS
        data_dirs = ["extensions", "i18n", "resources", "config", "core", "ui"]
        for d in data_dirs:
            dir_path = self.project_root / d
            if dir_path.exists():
                cmd.append(f"--add-data={dir_path}{os.pathsep}{d}")
                print(f"   {icon} 📦 Adicionando: {d}")
        
        for imp in config["hidden_imports"]:
            cmd.append("--hidden-import=" + imp)
        for exc in config["excludes"]:
            cmd.append("--exclude-module=" + exc)
        
        if platform_name == "Darwin":
            cmd.append("--osx-bundle-identifier=com.ardublock.studio")
        elif platform_name == "Linux":
            cmd.append("--strip")
        
        cmd.append(str(self.source_file))
        
        print(f"   {icon} 🔨 Compilando...")
        success, stdout, stderr = self._run_cmd(cmd)
        
        if success:
            if platform_name == "Darwin":
                apps = list(output_dir.glob("*.app"))
                if apps:
                    size = sum(f.stat().st_size for f in output_dir.rglob("*") if f.is_file()) / (1024*1024)
                    print(f"   {icon} ✅ {size:.1f} MB")
                    return True
            else:
                exe_path = output_dir / (config["name"] + config["ext"])
                if exe_path.exists():
                    size = exe_path.stat().st_size / (1024*1024)
                    print(f"   {icon} ✅ {size:.1f} MB")
                    self.cache[platform_name + "_" + self.source_hash] = {
                        "path": str(exe_path), "timestamp": self.timestamp, "size_mb": size
                    }
                    self._save_cache()
                    return True
        
        print(f"   {icon} ❌ Falha")
        if stderr:
            # Mostra últimas linhas de erro
            err_lines = stderr.strip().split('\n')
            print(f"   Erro (últimas linhas):")
            for line in err_lines[-10:]:
                print(f"      {line[:200]}")
        return False

    def _build_windows_via_wine(self):
        """Build Windows via Wine"""
        icon = "🪟"
        output_dir = self.build_dir / "windows"
        
        self._kill_wine_processes()
        
        wine = shutil.which("wine64") or shutil.which("wine")
        if not wine:
            print(f"   {icon} ❌ Wine nao encontrado")
            return False
        
        if self.wine_python_path and os.path.isfile(self.wine_python_path):
            wine_python = self.wine_python_path
            print(f"   {icon} 🐍 Python manual: {wine_python}")
        else:
            _, wine_python = self._find_wine_python()
        
        if not wine_python or not os.path.isfile(wine_python):
            print(f"   {icon} ❌ Python nao encontrado no Wine")
            self._create_windows_build_script()
            return False
        
        print(f"   {icon} 🐍 {wine_python}")
        print(f"   {icon} 📦 Instalando dependencias no Wine...")
        
        env = {
            **os.environ,
            "WINEDEBUG": "-all",
            "DISPLAY": ":0",
            "WINEPREFIX": os.path.dirname(os.path.dirname(os.path.dirname(wine_python)))
        }
        
        subprocess.run(
            [wine, wine_python, "-m", "pip", "install", "--quiet", "--no-cache-dir",
             "pyinstaller", "PyQt6", "PyQt6-WebEngine", "pyserial"],
            capture_output=True, text=True, timeout=300, env=env
        )
        
        # Criar script de build
        build_script = self.build_dir / "build_wine.py"
        output_win = "Z:" + str(output_dir).replace("/", "\\")
        source_win = "Z:" + str(self.source_file).replace("/", "\\")
        project_win = "Z:" + str(self.project_root).replace("/", "\\")
        
        script = f'''import sys, os
os.environ["WINEDEBUG"] = "-all"
sys.path.insert(0, r"{project_win}")

import PyInstaller.__main__
PyInstaller.__main__.run([
    "--onefile", "--windowed", "--clean", "--noconfirm",
    "--log-level=WARN",
    "--name=ArduBlockStudio",
    "--distpath=" + r"{output_win}",
    "--add-data=" + r"{project_win}\\extensions;extensions",
    "--add-data=" + r"{project_win}\\i18n;i18n",
    "--add-data=" + r"{project_win}\\resources;resources",
    "--hidden-import=PyQt6",
    "--hidden-import=PyQt6.QtCore",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=PyQt6.QtWebEngineWidgets",
    "--hidden-import=PyQt6.QtWebChannel",
    "--hidden-import=serial",
    "--exclude-module=tkinter",
    "--exclude-module=unittest",
    r"{source_win}"
])
'''
        build_script.write_text(script)
        
        print(f"   {icon} 🔨 Compilando (pode demorar 10-30 min)...")
        start = time.time()
        
        try:
            result = subprocess.run(
                [wine, wine_python, str(build_script)],
                capture_output=True, text=True, timeout=1800, env=env
            )
            elapsed = time.time() - start
            
            exe = output_dir / "ArduBlockStudio.exe"
            if exe.exists() and exe.stat().st_size > 5000000:
                size_mb = exe.stat().st_size / (1024*1024)
                print(f"\n   {icon} ✅ SUCESSO! ({elapsed:.0f}s, {size_mb:.1f} MB)")
                self.cache["Windows_" + self.source_hash] = {
                    "path": str(exe), "timestamp": self.timestamp, "size_mb": size_mb
                }
                self._save_cache()
                self._kill_wine_processes()
                return True
            
            print(f"\n   {icon} ❌ Falha ({elapsed:.0f}s)")
            if result.stderr:
                print(f"   Erro: {result.stderr[:500]}")
            
            self._kill_wine_processes()
        except subprocess.TimeoutExpired:
            print(f"\n   {icon} ⏱️ TIMEOUT")
            self._kill_wine_processes()
        except Exception as e:
            print(f"\n   {icon} ❌ Erro: {e}")
            self._kill_wine_processes()
        
        return False

    def _find_wine_python(self):
        """Procura Python no Wine"""
        wine = shutil.which("wine64") or shutil.which("wine")
        if not wine:
            return None, None
        
        wine_prefix = os.environ.get("WINEPREFIX", os.path.expanduser("~/.wine"))
        username = os.environ.get("USER", "iaiaia")
        
        print("   🔍 Procurando Python no Wine...")
        
        base = os.path.join(wine_prefix, "drive_c")
        search_paths = []
        
        for ver in ["310", "311", "312", "39", "38"]:
            ver_dot = ver[0] + "." + ver[1] if len(ver) >= 2 else ver
            
            candidates = [
                os.path.join(base, f"Python{ver_dot}", "python.exe"),
                os.path.join(base, f"Python{ver}", "python.exe"),
                os.path.join(base, "Program Files", f"Python{ver_dot}", "python.exe"),
                os.path.join(base, "Program Files (x86)", f"Python{ver_dot}", "python.exe"),
                os.path.join(base, "users", username, "Local Settings", 
                           "Application Data", "Programs", "Python", f"Python{ver_dot}", "python.exe"),
                os.path.join(base, "users", username, "AppData", 
                           "Local", "Programs", "Python", f"Python{ver_dot}", "python.exe"),
                os.path.join(base, "users", username, "AppData", 
                           "Roaming", "Python", f"Python{ver_dot}", "python.exe"),
            ]
            search_paths.extend(candidates)
        
        for path in search_paths:
            if os.path.isfile(path) and os.path.getsize(path) > 10000:
                print(f"   🐍 Encontrado: {path}")
                return wine, path
        
        return wine, None

    def _build_linux_via_wsl(self, output_dir):
        print("   🐧 Compilando via WSL...")
        return False

    def _build_linux_via_docker(self, output_dir):
        print("   🐧 Compilando via Docker...")
        return False

    def _create_windows_build_script(self):
        script = """@echo off
chcp 65001 >nul
echo ========================================
echo   ArduBlock Studio - Build Windows
echo ========================================
pip install pyinstaller PyQt6 PyQt6-WebEngine pyserial --quiet
pyinstaller --onefile --windowed --name ArduBlockStudio --clean --add-data "extensions;extensions" --add-data "i18n;i18n" --add-data "resources;resources" --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel --hidden-import=serial --exclude-module=tkinter --exclude-module=unittest main.py
if exist "dist\\ArduBlockStudio.exe" (echo ✅ SUCESSO!) else (echo ❌ FALHA)
pause
"""
        p = self.build_dir / "BUILD_WINDOWS.bat"
        p.write_text(script)
        print(f"   📝 Script: BUILD_WINDOWS.bat")

    def _create_macos_build_script(self):
        script = """#!/bin/bash
pip3 install pyinstaller PyQt6 PyQt6-WebEngine pyserial --quiet
pyinstaller --onefile --windowed --name ArduBlockStudio --clean --add-data "extensions:extensions" --add-data "i18n:i18n" --add-data "resources:resources" --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel --hidden-import=serial --exclude-module=tkinter --exclude-module=unittest --osx-bundle-identifier=com.ardublock.studio main.py
[ -d "dist/ArduBlockStudio.app" ] && echo "✅ SUCESSO!" || echo "❌ FALHA"
"""
        p = self.build_dir / "build_macos.sh"
        p.write_text(script)
        p.chmod(0o755)
        print(f"   📝 Script: build_macos.sh")

    def create_package(self, platform_name):
        icon = self.platform_configs[platform_name]["icon"]
        if platform_name == "Windows":
            exe = self.build_dir / "windows" / "ArduBlockStudio.exe"
            if exe.exists() and exe.stat().st_size > 5000000:
                zip_path = self.build_dir / f"ArduBlockStudio-{self.version}-windows-x64.zip"
                if not zip_path.exists():
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                        z.write(exe, "ArduBlockStudio.exe")
                print(f"   {icon} ✅ {zip_path.name} ({zip_path.stat().st_size/(1024*1024):.1f} MB)")
                return True
        elif platform_name == "Linux":
            exe = self.build_dir / "linux" / "ardublock-studio"
            if exe.exists() and exe.stat().st_size > 5000000:
                tar_path = self.build_dir / f"ardublock-studio-{self.version}-linux-x64.tar.gz"
                if not tar_path.exists():
                    with tarfile.open(tar_path, "w:gz") as tar:
                        tar.add(exe, "ardublock-studio/ardublock-studio")
                print(f"   {icon} ✅ {tar_path.name} ({tar_path.stat().st_size/(1024*1024):.1f} MB)")
                return True
        return False

    def print_header(self, targets):
        print("""
╔══════════════════════════════════════════════════════╗
║       ARDUBLOCK STUDIO BUILDER v3.6                  ║
╚══════════════════════════════════════════════════════╝
""")
        print(f"   🖥️  {self.current_os} | 🐍 {platform.python_version()} | 🎯 {', '.join(targets)}")
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="ArduBlock Studio Builder v3.6")
    parser.add_argument("--linux", action="store_true", help="Build Linux")
    parser.add_argument("--windows", action="store_true", help="Build Windows")
    parser.add_argument("--mac", action="store_true", help="Build macOS")
    parser.add_argument("--all", action="store_true", help="Build todas")
    parser.add_argument("--force", action="store_true", help="Forcar rebuild")
    parser.add_argument("--clean", action="store_true", help="Limpar cache")
    parser.add_argument("--wine-python", type=str, help="Path do python.exe no Wine")
    
    args = parser.parse_args()
    
    try:
        packager = UniversalPackager(wine_python_path=args.wine_python)
        
        if args.clean and packager.cache_dir.exists():
            shutil.rmtree(packager.cache_dir)
            packager.cache_dir.mkdir()
            packager.cache = {}
            print("🗑️  Cache limpo\n")
        
        targets = []
        if args.linux: targets.append("Linux")
        if args.windows: targets.append("Windows")
        if args.mac: targets.append("macOS")
        if args.all: targets = ["Linux", "Windows", "macOS"]
        if not targets:
            current = {"Linux": "Linux", "Windows": "Windows", "Darwin": "macOS"}
            targets = [current.get(packager.current_os, "Linux")]
        
        packager.print_header(targets)
        wine_ok, docker_ok, wsl_ok = packager.check_dependencies()
        
        results = {}
        for t in targets:
            if t == "Linux":
                results["Linux"] = packager.build_linux(args.force, wine_ok, docker_ok, wsl_ok)
            elif t == "Windows":
                results["Windows"] = packager.build_windows(args.force, wine_ok, docker_ok)
            elif t == "macOS":
                results["macOS"] = packager.build_macos(args.force, docker_ok)
        
        print("\n" + "=" * 60)
        print("📦 PACOTES")
        print("=" * 60)
        for t in targets:
            plat = t if t != "macOS" else "Darwin"
            packager.create_package(plat)
        
        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("=" * 60)
        for plat, ok in results.items():
            icon = packager.platform_configs[plat if plat != "macOS" else "Darwin"]["icon"]
            print(f"   {icon} {plat:12} {'✅' if ok else '❌'}")
        print(f"\n   📁 {packager.build_dir.absolute()}")
        print("=" * 60)
        
        return 0 if all(results.values()) else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido")
        subprocess.run(["wineserver", "-k"], capture_output=True)
        return 130
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())