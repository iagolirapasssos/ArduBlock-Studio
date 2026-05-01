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
        self.source_file = self.project_root / "main.py"
        self.current_os = platform.system()
        self.version = "3.6.0"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wine_python_path = wine_python_path
        
        if not self.source_file.exists():
            print("❌ ERRO: main.py nao encontrado!")
            sys.exit(1)
        
        self.source_hash = hashlib.md5(self.source_file.read_bytes()).hexdigest()[:12]
        
        self.platform_configs = {
            "Windows": {
                "name": "ArduBlockStudio", "ext": ".exe", "icon": "🪟",
                "hidden_imports": ["PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", 
                    "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel",
                    "serial", "json", "tempfile", "shutil", "threading",
                    "subprocess", "glob", "pathlib", "platform"],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            },
            "Darwin": {
                "name": "ArduBlockStudio", "ext": ".app", "icon": "🍎",
                "hidden_imports": ["PyQt6", "PyQt6.QtCore", "PyQt6.QtGui",
                    "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel",
                    "serial", "json", "tempfile", "shutil", "threading",
                    "subprocess", "glob", "pathlib", "platform"],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            },
            "Linux": {
                "name": "ardublock-studio", "ext": "", "icon": "🐧",
                "hidden_imports": ["PyQt6", "PyQt6.QtCore", "PyQt6.QtGui",
                    "PyQt6.QtWidgets", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebChannel",
                    "serial", "json", "tempfile", "shutil", "threading",
                    "subprocess", "glob", "pathlib", "platform"],
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

    def _kill_wine_processes(self):
        """Mata todos os processos Wine pendentes"""
        try:
            subprocess.run(["wineserver", "-k"], capture_output=True, timeout=10)
            time.sleep(2)
            print("   🍷 Processos Wine limpos")
        except:
            pass

    def _find_wine_python(self):
        """Procura Python no Wine em TODOS os locais possíveis"""
        wine = shutil.which("wine64") or shutil.which("wine")
        if not wine:
            return None, None
        
        wine_prefix = os.environ.get("WINEPREFIX", os.path.expanduser("~/.wine"))
        username = os.environ.get("USER", "iaiaia")
        
        print("   🔍 Procurando Python no Wine...")
        
        # Lista COMPLETA de paths - inclui o caminho específico do usuário
        base = os.path.join(wine_prefix, "drive_c")
        search_paths = []
        
        for ver in ["310", "311", "312", "39", "38"]:
            ver_dot = ver[0] + "." + ver[1] if len(ver) >= 2 else ver
            
            candidates = [
                # Instalação padrão
                os.path.join(base, f"Python{ver_dot}", "python.exe"),
                os.path.join(base, f"Python{ver}", "python.exe"),
                # Program Files
                os.path.join(base, "Program Files", f"Python{ver_dot}", "python.exe"),
                os.path.join(base, "Program Files (x86)", f"Python{ver_dot}", "python.exe"),
                # Local Settings (caminho do usuário)
                os.path.join(base, "users", username, "Local Settings", 
                           "Application Data", "Programs", "Python", f"Python{ver_dot}", "python.exe"),
                # AppData
                os.path.join(base, "users", username, "AppData", 
                           "Local", "Programs", "Python", f"Python{ver_dot}", "python.exe"),
                # AppData com Roaming
                os.path.join(base, "users", username, "AppData", 
                           "Roaming", "Python", f"Python{ver_dot}", "python.exe"),
            ]
            search_paths.extend(candidates)
        
        # Verifica cada path
        for path in search_paths:
            if os.path.isfile(path) and os.path.getsize(path) > 10000:
                print(f"   🐍 Encontrado: {path}")
                return wine, path
        
        # Busca com find
        print("   🔍 Busca profunda...")
        try:
            result = subprocess.run(
                ["find", wine_prefix, "-path", "*/Python*/python.exe", "-type", "f", "-size", "+10k"],
                capture_output=True, text=True, timeout=20
            )
            if result.returncode == 0 and result.stdout.strip():
                paths = [p for p in result.stdout.strip().split('\n') if p]
                # Prefere Python 3.10
                for p in paths:
                    if 'Python310' in p or 'Python3.10' in p:
                        print(f"   🐍 Encontrado: {p}")
                        return wine, p
                if paths:
                    print(f"   🐍 Encontrado: {paths[0]}")
                    return wine, paths[0]
        except:
            pass
        
        return wine, None

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
        return False

    def _build_windows_via_wine(self):
        """Build Windows via Wine - VERSÃO ROBUSTA COM TIMEOUT"""
        icon = "🪟"
        output_dir = self.build_dir / "windows"
        
        # Mata processos Wine antigos
        self._kill_wine_processes()
        
        wine = shutil.which("wine64") or shutil.which("wine")
        if not wine:
            print(f"   {icon} ❌ Wine nao encontrado")
            return False
        
        # Determina Python no Wine
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
        
        # Instala dependências COM TIMEOUT e sem output excessivo
        print(f"   {icon} 📦 Instalando PyInstaller + PyQt6 (2-5 min)...")
        
        env = {
            **os.environ,
            "WINEDEBUG": "-all",      # Suprime warnings
            "DISPLAY": ":0",
            "WINEPREFIX": os.path.dirname(os.path.dirname(os.path.dirname(wine_python)))
        }
        
        pip_result = subprocess.run(
            [wine, wine_python, "-m", "pip", "install", "--quiet", "--no-cache-dir",
             "--disable-pip-version-check",
             "pyinstaller", "PyQt6", "PyQt6-WebEngine", "pyserial"],
            capture_output=True, text=True, timeout=300, env=env
        )
        
        if pip_result.returncode != 0:
            print(f"   {icon} ⚠️ Aviso na instalacao, continuando...")
        
        # Cria script de build
        build_script = self.build_dir / "build_wine.py"
        
        # Caminhos no formato Windows
        output_win = "Z:" + str(output_dir).replace("/", "\\")
        source_win = "Z:" + str(self.source_file).replace("/", "\\")
        
        script = '''import sys, os
os.environ["WINEDEBUG"] = "-all"
sys.path.insert(0, r"{}")
import PyInstaller.__main__
PyInstaller.__main__.run([
    "--onefile", "--windowed", "--clean", "--noconfirm",
    "--log-level=WARN",
    "--name=ArduBlockStudio",
    "--distpath=" + r"{}",
    "--hidden-import=PyQt6",
    "--hidden-import=PyQt6.QtCore",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=PyQt6.QtWebEngineWidgets",
    "--hidden-import=PyQt6.QtWebChannel",
    "--hidden-import=serial",
    "--exclude-module=tkinter",
    "--exclude-module=unittest",
    r"{}"
])
'''.format(str(self.source_file.parent).replace("\\", "\\\\"), output_win, source_win)
        
        build_script.write_text(script)
        
        # EXECUTA O BUILD
        print(f"   {icon} 🔨 Compilando (10-30 min, aguarde)...")
        print(f"   {icon} ⏳ Nao feche esta janela!")
        
        start = time.time()
        
        try:
            result = subprocess.run(
                [wine, wine_python, str(build_script)],
                capture_output=True, text=True, timeout=1800,  # 30 minutos
                env=env
            )
            elapsed = time.time() - start
            
            # Verifica sucesso
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
            
            # Falhou - mostra output
            print(f"\n   {icon} ❌ Falha ({elapsed:.0f}s)")
            
            if result.stdout:
                lines = [l for l in result.stdout.split('\n') if l.strip()]
                if lines:
                    print(f"   📋 Ultimas linhas:")
                    for line in lines[-10:]:
                        print(f"      {line[:150]}")
            
            if result.stderr:
                errors = [l for l in result.stderr.split('\n') if 'Error' in l or 'ERROR' in l]
                if errors:
                    print(f"   ❌ Erros:")
                    for err in errors[-5:]:
                        print(f"      {err[:150]}")
            
            self._kill_wine_processes()
            
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            print(f"\n   {icon} ⏱️ TIMEOUT ({elapsed:.0f}s)")
            self._kill_wine_processes()
        
        except Exception as e:
            print(f"\n   {icon} ❌ Erro: {e}")
            self._kill_wine_processes()
        
        self._create_windows_build_script()
        return False

    def _run_cmd(self, cmd, timeout=600):
        """Executa comando simples"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except:
            return False, "", ""

    def _build_linux_via_wsl(self, output_dir):
        print("   🐧 🪟 WSL...")
        source = str(self.source_file.parent).replace("\\", "/")
        out = str(output_dir).replace("\\", "/")
        cmd = (f"cd {source} && pip3 install --quiet pyinstaller PyQt6 PyQt6-WebEngine pyserial 2>/dev/null; "
               f"pyinstaller --onefile --windowed --name ardublock-studio --strip main.py && "
               f"cp dist/ardublock-studio {out}/")
        subprocess.run(["wsl", "bash", "-c", cmd], capture_output=True, timeout=600)
        exe = output_dir / "ardublock-studio"
        if exe.exists():
            os.chmod(exe, 0o755)
            return True
        return False

    def _build_linux_via_docker(self, output_dir):
        return False

    def _create_windows_build_script(self):
        script = """@echo off
chcp 65001 >nul
echo ========================================
echo   ArduBlock Studio - Build Windows
echo ========================================
echo.
pip install pyinstaller PyQt6 PyQt6-WebEngine pyserial --quiet
echo.
pyinstaller --onefile --windowed --name ArduBlockStudio --clean --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel --hidden-import=serial --exclude-module=tkinter --exclude-module=unittest main.py
echo.
if exist "dist\\ArduBlockStudio.exe" (echo ✅ SUCESSO! dist\\ArduBlockStudio.exe) else (echo ❌ FALHA)
pause
"""
        (self.build_dir / "BUILD_WINDOWS.bat").write_text(script)
        print(f"   📝 Script: BUILD_WINDOWS.bat")

    def _create_macos_build_script(self):
        script = """#!/bin/bash
pip3 install pyinstaller PyQt6 PyQt6-WebEngine pyserial --quiet
pyinstaller --onefile --windowed --name ArduBlockStudio --clean --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel --hidden-import=serial --exclude-module=tkinter --exclude-module=unittest --osx-bundle-identifier=com.ardublock.studio main.py
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
        # Mata Wine ao sair
        subprocess.run(["wineserver", "-k"], capture_output=True)
        return 130
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())