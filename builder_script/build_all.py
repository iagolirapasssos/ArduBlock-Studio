#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empacotador Universal do ArduBlock Studio v3.6
COM SUPORTE PARA BUILD SEM LIMITE DE TEMPO
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
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta

class LicenseManager:
    """Gerenciador de licenças temporais (OPCIONAL)"""
    
    @staticmethod
    def generate_license_key(duration_str):
        """
        Gera uma chave de licença criptografada
        """
        duration_seconds = LicenseManager._parse_duration(duration_str)
        expiration_date = datetime.now() + timedelta(seconds=duration_seconds)
        
        payload = {
            'expiration': expiration_date.isoformat(),
            'duration': duration_str,
            'timestamp': datetime.now().isoformat(),
            'first_run': True
        }
        
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = f.encrypt(json.dumps(payload).encode())
        
        import base64
        license_data = base64.b64encode(key + b'::' + encrypted).decode()
        
        return license_data, expiration_date
    
    @staticmethod
    def _parse_duration(duration_str):
        """Converte string de duração para segundos"""
        match = re.match(r'(\d+)\s*(min|hour|day|month|year|sec|second|minute)s?', 
                        duration_str.lower().strip())
        
        if not match:
            raise ValueError("Formato invalido: " + duration_str)
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit in ['sec', 'second']:
            return value
        elif unit in ['min', 'minute']:
            return value * 60
        elif unit == 'hour':
            return value * 3600
        elif unit == 'day':
            return value * 86400
        elif unit == 'month':
            return value * 86400 * 30
        elif unit == 'year':
            return value * 86400 * 365
        
        return value * 86400

    @staticmethod
    def generate_unlimited_license():
        """Gera uma licença sem limite de tempo"""
        payload = {
            'expiration': 'unlimited',
            'type': 'perpetual',
            'timestamp': datetime.now().isoformat(),
            'first_run': True,
            'unlimited': True
        }
        
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        f = Fernet(key)
        encrypted = f.encrypt(json.dumps(payload).encode())
        
        import base64
        license_data = base64.b64encode(key + b'::' + encrypted).decode()
        
        return license_data, None  # None = sem expiração


class UniversalPackager:
    def __init__(self, wine_python_path=None, license_duration=None, unlimited=False):
        self.project_root = Path(__file__).parent.resolve()
        self.build_dir = self.project_root / "dist"
        self.cache_dir = self.build_dir / ".cache"
        self.source_file = self.project_root / "main.py"
        self.current_os = platform.system()
        self.version = "3.6.0"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wine_python_path = wine_python_path
        self.license_duration = license_duration
        self.unlimited = unlimited  # NOVO: flag para build sem limite
        self._backup_file = None
        
        self.license_filename = "ardublock_license.key"
        
        if not self.source_file.exists():
            print("X ERRO: " + str(self.source_file) + " nao encontrado!")
            sys.exit(1)
        
        # Detectar codificação do arquivo
        self.source_encoding = self._detect_encoding()
        print("INFO Codificacao detectada: " + self.source_encoding)
        
        # Ler com a codificação correta
        source_bytes = self.source_file.read_bytes()
        self.source_hash = hashlib.md5(source_bytes).hexdigest()[:12]
        
        self.license_key = None
        self.license_expiration = None
        
        # LÓGICA MODIFICADA: Se for unlimited, NÃO injeta código de licença
        if self.unlimited:
            print("🔓 BUILD SEM LIMITE DE TEMPO ATIVADO")
            print("   O aplicativo será gerado sem restrições de licença")
            # Gera uma licença "unlimited" se ainda quiser ter um arquivo de licença
            self.license_key, self.license_expiration = LicenseManager.generate_unlimited_license()
            
        elif self.license_duration:
            self.license_key, self.license_expiration = \
                LicenseManager.generate_license_key(self.license_duration)
            
            license_info = {
                'key': self.license_key,
                'duration': self.license_duration,
                'expiration': self.license_expiration.isoformat(),
                'generated_at': datetime.now().isoformat()
            }
            
            license_dir = self.build_dir / "licenses"
            license_dir.mkdir(parents=True, exist_ok=True)
            
            license_file = license_dir / ("license_" + self.timestamp + ".json")
            license_file.write_text(json.dumps(license_info, indent=2))
            
            print("CHAVE Licenca gerada: " + self.license_duration)
            print("CALENDARIO Expira em: " + self.license_expiration.strftime('%Y-%m-%d %H:%M:%S'))
        
        self.platform_configs = {
            "Windows": {
                "name": "ArduBlockStudio", "ext": ".exe", "icon": "[W]",
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
                    "cryptography.fernet", "base64", "hashlib", "uuid",
                ],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            },
            "Darwin": {
                "name": "ArduBlockStudio", "ext": ".app", "icon": "[M]",
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
                    "cryptography.fernet", "base64", "hashlib", "uuid",
                ],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            },
            "Linux": {
                "name": "ardublock-studio", "ext": "", "icon": "[L]",
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
                    "cryptography.fernet", "base64", "hashlib", "uuid",
                ],
                "excludes": ["tkinter", "unittest", "email", "http", "xmlrpc"]
            }
        }
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        for plat in ["windows", "macos", "linux"]:
            (self.build_dir / plat).mkdir(exist_ok=True)
        
        self.cache = self._load_cache()
        
        # SÓ injeta código de licença se NÃO for unlimited e license_duration estiver definido
        if not self.unlimited and self.license_duration:
            self._inject_license_code()
        elif self.unlimited:
            print("🔓 Build sem limite: Pulando injeção de código de licença")
            # Opcional: injetar código sem verificação
            self._inject_no_license_code()

    def _inject_no_license_code(self):
        """Injeta uma versão simplificada SEM verificação de licença"""
        source_content = self._read_source()
        
        # Salvar backup
        backup_file = self.project_root / "main.py.backup"
        backup_file.write_bytes(self.source_file.read_bytes())
        self._backup_file = backup_file
        
        # Código que NÃO verifica licença (apenas passa direto)
        no_license_code = '''
    # ===== BUILD SEM LIMITE DE TEMPO (UNLIMITED VERSION) =====
    def _verificar_licenca_ardublock():
        """Versão sem verificação de licença - UNLIMITED"""
        print("[INFO] Versão sem limite de tempo - UNLIMITED")
        return True

    # Chamada sem verificação
    _verificar_licenca_ardublock()
    # ===== FIM DA VERSÃO UNLIMITED =====
    '''
        
        lines = source_content.split('\n')
        inject_index = len(lines)
        
        for i, line in enumerate(lines):
            if 'if __name__' in line and '__main__' in line:
                inject_index = i
                break
        
        if inject_index < len(lines):
            lines.insert(inject_index, no_license_code)
            modified_content = '\n'.join(lines)
        else:
            modified_content = source_content + '\n' + no_license_code
        
        self._write_source(modified_content)
        print("🔓 Codigo UNLIMITED injetado (sem verificacao de licenca)")

    def _detect_encoding(self):
        """Detecta a codificação do arquivo main.py"""
        try:
            self.source_file.read_text(encoding='utf-8')
            return 'utf-8'
        except:
            pass
        
        try:
            self.source_file.read_text(encoding='latin-1')
            return 'latin-1'
        except:
            pass
        
        try:
            self.source_file.read_text(encoding='cp1252')
            return 'cp1252'
        except:
            pass
        
        try:
            import chardet
            raw_data = self.source_file.read_bytes()
            result = chardet.detect(raw_data)
            if result['encoding']:
                return result['encoding']
        except ImportError:
            pass
        
        return 'utf-8'

    def _read_source(self):
        """Lê o arquivo fonte com a codificação detectada"""
        try:
            return self.source_file.read_text(encoding=self.source_encoding)
        except:
            raw = self.source_file.read_bytes()
            return raw.decode(self.source_encoding, errors='replace')

    def _write_source(self, content):
        """Escreve no arquivo fonte SEMPRE como UTF-8 para compatibilidade com PyInstaller"""
        self.source_file.write_text(content, encoding='utf-8')
        self.source_encoding = 'utf-8'

    def _inject_license_code(self):
        """Injeta o código de verificação de licença no main.py (VERSÃO COMPLETA)"""
        source_content = self._read_source()
        
        # Salvar backup dos bytes originais
        backup_file = self.project_root / "main.py.backup"
        backup_file.write_bytes(self.source_file.read_bytes())
        self._backup_file = backup_file
        
        lines = source_content.split('\n')
        inject_index = len(lines)
        
        for i, line in enumerate(lines):
            if 'if __name__' in line and '__main__' in line:
                inject_index = i
                break
        
        # Código de licenciamento completo (mantido do original)
        license_code = '''
    # ===== SISTEMA DE LICENCIAMENTO TEMPORAL =====
    def _verificar_licenca_ardublock():
        """Verifica a licenca do ArduBlock Studio"""
        import sys as _sys, os as _os, json as _json, base64 as _base64, hashlib as _hashlib, uuid as _uuid
        from datetime import datetime as _datetime
        from pathlib import Path as _Path
        
        class _SistemaLicenciamento:
            def __init__(self):
                if getattr(_sys, 'frozen', False):
                    self.app_dir = _Path(_sys.executable).parent
                else:
                    self.app_dir = _Path.cwd()
                
                self.license_file = None
                self.first_run_file = self.app_dir / "ardublock_installed.dat"
                self.machine_id = self._gerar_id_maquina()
                self._localizar_arquivo_licenca()
            
            def _gerar_id_maquina(self):
                try:
                    import platform as _platform
                    info = []
                    if _sys.platform == 'win32':
                        info.append(_os.environ.get('COMPUTERNAME', ''))
                        info.append(_os.environ.get('USERNAME', ''))
                    else:
                        info.append(_os.uname().nodename if hasattr(_os, 'uname') else '')
                        info.append(_os.environ.get('USER', ''))
                    
                    info.append(_platform.node() if hasattr(_platform, 'node') else '')
                    info.append(str(_uuid.getnode()))
                    
                    combined = '|'.join(info)
                    return _hashlib.sha256(combined.encode()).hexdigest()[:16]
                except:
                    return str(_uuid.uuid4())[:16]
            
            def _localizar_arquivo_licenca(self):
                possiveis_nomes = ["ardublock_license.key", ".ardublock_license"]
                possiveis_locais = [
                    self.app_dir,
                    _Path.home() / ".ardublock",
                    _Path.home() / "AppData" / "Local" / "ArduBlockStudio",
                    _Path("/tmp") if _sys.platform != 'win32' else None
                ]
                
                for local in possiveis_locais:
                    if local is None:
                        continue
                    for nome in possiveis_nomes:
                        arquivo = local / nome
                        if arquivo.exists():
                            self.license_file = arquivo
                            return
            
            def verificar_primeira_execucao(self):
                if self.first_run_file.exists():
                    try:
                        data = _json.loads(self.first_run_file.read_text())
                        if data.get('machine_id') == self.machine_id:
                            return False
                    except:
                        pass
                
                self._registrar_instalacao()
                return True
            
            def _registrar_instalacao(self):
                try:
                    dados_instalacao = {
                        'machine_id': self.machine_id,
                        'first_run': _datetime.now().isoformat(),
                        'platform': _sys.platform,
                        'version': '3.6.0'
                    }
                    self.first_run_file.write_text(_json.dumps(dados_instalacao))
                    
                    try:
                        local_alternativo = _Path.home() / ".ardublock" / "installed.dat"
                        local_alternativo.parent.mkdir(parents=True, exist_ok=True)
                        local_alternativo.write_text(_json.dumps(dados_instalacao))
                    except:
                        pass
                except:
                    pass
            
            def verificar_licenca(self):
                try:
                    if not self.license_file or not self.license_file.exists():
                        return False
                    
                    encrypted_data = self.license_file.read_text()
                    
                    try:
                        from cryptography.fernet import Fernet as _Fernet
                        key_data = _base64.b64decode(encrypted_data)
                        key, encrypted = key_data.split(b'::', 1)
                        f = _Fernet(key)
                        decrypted = f.decrypt(encrypted)
                    except:
                        return False
                    
                    license_data = _json.loads(decrypted)
                    
                    # Verifica se é licença unlimited
                    if license_data.get('unlimited') or license_data.get('expiration') == 'unlimited':
                        return True
                    
                    expiration = _datetime.fromisoformat(license_data['expiration'])
                    
                    if 'machine_id' in license_data and license_data['machine_id'] != self.machine_id:
                        return False
                    
                    if 'first_run' in license_data and license_data.get('first_run') == True:
                        license_data['machine_id'] = self.machine_id
                        license_data['first_run'] = False
                        
                        from cryptography.fernet import Fernet as _Fernet
                        key = _Fernet.generate_key()
                        f = _Fernet(key)
                        encrypted = f.encrypt(_json.dumps(license_data).encode())
                        license_data_encoded = _base64.b64encode(key + b'::' + encrypted).decode()
                        self.license_file.write_text(license_data_encoded)
                    
                    if _datetime.now() > expiration:
                        return False
                    
                    return True
                    
                except:
                    return False
            
            def mostrar_modal_expiracao(self):
                from PyQt6.QtWidgets import QApplication as _QApplication, QMessageBox as _QMessageBox
                from PyQt6.QtCore import Qt as _Qt
                
                app = _QApplication.instance()
                if not app:
                    app = _QApplication(_sys.argv)
                
                expiration_date = "Data nao encontrada"
                try:
                    if self.license_file and self.license_file.exists():
                        from cryptography.fernet import Fernet as _Fernet
                        encrypted_data = self.license_file.read_text()
                        key_data = _base64.b64decode(encrypted_data)
                        key, encrypted = key_data.split(b'::', 1)
                        f = _Fernet(key)
                        decrypted = f.decrypt(encrypted)
                        license_data = _json.loads(decrypted)
                        if license_data.get('expiration') != 'unlimited':
                            expiration_date = _datetime.fromisoformat(license_data['expiration']).strftime('%d/%m/%Y %H:%M:%S')
                        else:
                            return  # Licença unlimited não mostra expiração
                except:
                    pass
                
                msg = _QMessageBox()
                msg.setIcon(_QMessageBox.Icon.Critical)
                msg.setWindowTitle("LICENCA EXPIRADA / LICENSE EXPIRED")
                
                mensagem = (
                    "=======================================================\\n"
                    "        LICENCA EXPIRADA / LICENSE EXPIRED\\n"
                    "=======================================================\\n\\n"
                    "[PT-BR]\\n"
                    "Sua licenca de uso do ArduBlock Studio expirou!\\n"
                    "Data de expiracao: " + expiration_date + "\\n\\n"
                    "O aplicativo sera desinstalado automaticamente.\\n"
                    "Para continuar utilizando, solicite uma nova licenca.\\n\\n"
                    "Contato para renovacao:\\n"
                    "  Nome: Francisco Iago Lira Passos\\n"
                    "  Cargo: Professor / Desenvolvedor\\n"
                    "  E-mail: prof.iagolirapassos@gmail.com\\n\\n"
                    "-------------------------------------------------------\\n\\n"
                    "[EN-US]\\n"
                    "Your ArduBlock Studio license has expired!\\n"
                    "Expiration date: " + expiration_date + "\\n\\n"
                    "The application will be uninstalled automatically.\\n"
                    "To continue using, please request a new license.\\n\\n"
                    "Contact for renewal:\\n"
                    "  Name: Francisco Iago Lira Passos\\n"
                    "  Role: Professor / Developer\\n"
                    "  E-mail: prof.iagolirapassos@gmail.com\\n\\n"
                    "======================================================="
                )
                
                msg.setText(mensagem)
                msg.setInformativeText(
                    "Clique OK para fechar e desinstalar o aplicativo.\\n"
                    "Click OK to close and uninstall the application."
                )
                msg.setStandardButtons(_QMessageBox.StandardButton.Ok)
                msg.setWindowFlags(msg.windowFlags() | _Qt.WindowType.WindowStaysOnTopHint)
                msg.setMinimumWidth(650)
                msg.setMinimumHeight(550)
                
                msg.exec()
                self._auto_destruir()
            
            def _auto_destruir(self):
                import tempfile as _tempfile
                
                try:
                    if getattr(_sys, 'frozen', False):
                        app_path = str(_Path(_sys.executable))
                        app_dir = str(_Path(_sys.executable).parent)
                        
                        arquivos_remover = [
                            self.first_run_file,
                            self.license_file,
                            _Path.home() / ".ardublock" / "installed.dat"
                        ]
                        
                        for arquivo in arquivos_remover:
                            try:
                                if arquivo and arquivo.exists():
                                    arquivo.unlink()
                            except:
                                pass
                        
                        if _sys.platform == 'win32':
                            linhas_script = [
                                '@echo off',
                                'ping 127.0.0.1 -n 3 >nul',
                                'del /f /q "' + app_path + '"',
                                'rmdir /s /q "' + app_dir + '" 2>nul',
                                'del /f /q "%~f0"'
                            ]
                            script_content = '\\n'.join(linhas_script)
                            script_path = str(_Path(_tempfile.gettempdir()) / "ardublock_cleanup.bat")
                            with open(script_path, 'w') as f:
                                f.write(script_content)
                            _os.system('start /B cmd /c "' + script_path + '"')
                            
                        elif _sys.platform == 'darwin':
                            linhas_script = [
                                '#!/bin/bash',
                                'sleep 3',
                                'rm -rf "' + app_dir + '"',
                                'rm -f "$0"'
                            ]
                            script_content = '\\n'.join(linhas_script)
                            script_path = str(_Path(_tempfile.gettempdir()) / "ardublock_cleanup.sh")
                            with open(script_path, 'w') as f:
                                f.write(script_content)
                            _os.chmod(script_path, 0o755)
                            _os.system('bash "' + script_path + '" &')
                            
                        else:
                            linhas_script = [
                                '#!/bin/bash',
                                'sleep 3',
                                'rm -f "' + app_path + '"',
                                'rm -rf "' + app_dir + '"',
                                'rm -f "$0"'
                            ]
                            script_content = '\\n'.join(linhas_script)
                            script_path = str(_Path(_tempfile.gettempdir()) / "ardublock_cleanup.sh")
                            with open(script_path, 'w') as f:
                                f.write(script_content)
                            _os.chmod(script_path, 0o755)
                            _os.system('bash "' + script_path + '" &')
                        
                except:
                    pass
                
                _sys.exit(1)
        
        # Executar verificacao
        _sistema_licenca = _SistemaLicenciamento()
        _primeira_execucao = _sistema_licenca.verificar_primeira_execucao()
        
        if not _sistema_licenca.verificar_licenca():
            _sistema_licenca.mostrar_modal_expiracao()
            _sys.exit(1)
        
        return True

    # Chamar verificacao de licenca
    _verificar_licenca_ardublock()
    # ===== FIM DO SISTEMA DE LICENCIAMENTO =====

    '''
        
        if inject_index < len(lines):
            lines.insert(inject_index, license_code)
            modified_content = '\n'.join(lines)
        else:
            modified_content = source_content + '\n' + license_code
        
        # SEMPRE salvar como UTF-8 para compatibilidade com PyInstaller
        self._write_source(modified_content)
        print("PINCEL Codigo de licenciamento injetado no main.py")
        print("   [OK] Arquivo convertido para UTF-8")
        print("   [OK] Verificacao em tempo de execucao configurada")
        print("   [OK] Deteccao de primeira execucao ativada")
        print("   [OK] Vinculacao de licenca por maquina ativada")

    def restore_source(self):
        """Restaura o arquivo main.py original preservando a codificação original"""
        if self._backup_file and self._backup_file.exists():
            original_bytes = self._backup_file.read_bytes()
            self.source_file.write_bytes(original_bytes)
            self._backup_file.unlink()
            # Re-detectar codificação após restaurar
            self.source_encoding = self._detect_encoding()
            print("[OK] main.py restaurado ao original (codificacao: " + self.source_encoding + ")")

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
            return False, "", "Timeout after " + str(timeout) + "s"
        except Exception as e:
            return False, "", str(e)

    def _kill_wine_processes(self):
        """Mata todos os processos Wine pendentes"""
        try:
            subprocess.run(["wineserver", "-k"], capture_output=True, timeout=10)
            time.sleep(2)
            print("   [OK] Processos Wine limpos")
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
            print("   " + config['icon'] + " [CACHE] Ja existe: " + Path(path).name + " (" + "{:.1f}".format(size_mb) + " MB)")
            return True
        return False

    def check_dependencies(self):
        print("=" * 60)
        print("[DEP] VERIFICANDO DEPENDENCIAS")
        print("=" * 60)
        
        try:
            import PyInstaller
            print("   [OK] PyInstaller")
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("   [OK] PyInstaller instalado")
        
        try:
            import cryptography
            print("   [OK] cryptography")
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "cryptography"], check=True)
            print("   [OK] cryptography instalado")
        
        wine_ok = False
        if self.current_os != "Windows":
            if shutil.which("wine") or shutil.which("wine64"):
                print("   [OK] Wine")
                wine_ok = True
            else:
                print("   [AVISO] Wine nao instalado")
        
        docker_ok = shutil.which("docker") is not None
        if docker_ok:
            print("   [OK] Docker")
        
        wsl_ok = self.current_os == "Windows" and shutil.which("wsl") is not None
        print()
        return wine_ok, docker_ok, wsl_ok

    def build_linux(self, force=False, wine_ok=False, docker_ok=False, wsl_ok=False):
        icon = "[L]"
        print("\n" + "=" * 60)
        print(icon + " BUILD LINUX")
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
        icon = "[W]"
        print("\n" + "=" * 60)
        print(icon + " BUILD WINDOWS")
        print("=" * 60)
        
        if not force and self._should_skip("Windows"):
            return True
        
        if self.current_os == "Windows":
            return self._pyinstaller_build("Windows", self.build_dir / "windows")
        elif wine_ok:
            return self._build_windows_via_wine()
        else:
            print("   " + icon + " [AVISO] Wine necessario para cross-compile")
            self._create_windows_build_script()
            return False

    def build_macos(self, force=False, docker_ok=False):
        icon = "[M]"
        print("\n" + "=" * 60)
        print(icon + " BUILD macOS")
        print("=" * 60)
        
        if not force and self._should_skip("macOS"):
            return True
        
        if self.current_os == "Darwin":
            return self._pyinstaller_build("Darwin", self.build_dir / "macos")
        else:
            print("   " + icon + " [AVISO] Requer macOS para build")
            self._create_macos_build_script()
            return False

    def _copy_license_to_build(self, platform_name, output_dir):
        """Copia arquivo de licença para o diretório de build"""
        if self.license_key:
            if platform_name == "Darwin":
                apps = list(output_dir.glob("*.app"))
                if apps:
                    app_dir = apps[0] / "Contents" / "MacOS"
                    license_path = app_dir / self.license_filename
                else:
                    return
            else:
                license_path = output_dir / self.license_filename
            
            try:
                with open(str(license_path), 'w', encoding='utf-8') as f:
                    f.write(self.license_key)
                
                if platform_name == "Windows":
                    try:
                        import ctypes
                        ctypes.windll.kernel32.SetFileAttributesW(str(license_path), 2)
                    except:
                        pass
                
                if self.unlimited:
                    print("   🔓 [KEY] Licenca UNLIMITED incluida")
                else:
                    print("   [KEY] Licenca incluida: " + self.license_duration)
                    print("   [CAL] Expiracao: " + self.license_expiration.strftime('%Y-%m-%d %H:%M'))
            except Exception as e:
                print("   [ERRO] Falha ao copiar licenca: " + str(e))

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
        
        data_dirs = ["extensions", "i18n", "resources", "config", "core", "ui"]
        for d in data_dirs:
            dir_path = self.project_root / d
            if dir_path.exists():
                cmd.append("--add-data=" + str(dir_path) + os.pathsep + d)
                print("   " + icon + " [DATA] Adicionando: " + d)
        
        for imp in config["hidden_imports"]:
            cmd.append("--hidden-import=" + imp)
        for exc in config["excludes"]:
            cmd.append("--exclude-module=" + exc)
        
        if platform_name == "Darwin":
            cmd.append("--osx-bundle-identifier=com.ardublock.studio")
        elif platform_name == "Linux":
            cmd.append("--strip")
        
        cmd.append(str(self.source_file))
        
        print("   " + icon + " [BUILD] Compilando...")
        success, stdout, stderr = self._run_cmd(cmd)
        
        if success:
            self._copy_license_to_build(platform_name, output_dir)
            
            if platform_name == "Darwin":
                apps = list(output_dir.glob("*.app"))
                if apps:
                    size = sum(f.stat().st_size for f in output_dir.rglob("*") if f.is_file()) / (1024*1024)
                    print("   " + icon + " [OK] " + "{:.1f}".format(size) + " MB")
                    return True
            else:
                exe_path = output_dir / (config["name"] + config["ext"])
                if exe_path.exists():
                    size = exe_path.stat().st_size / (1024*1024)
                    print("   " + icon + " [OK] " + "{:.1f}".format(size) + " MB")
                    self.cache[platform_name + "_" + self.source_hash] = {
                        "path": str(exe_path), "timestamp": self.timestamp, "size_mb": size
                    }
                    self._save_cache()
                    return True
        
        print("   " + icon + " [ERRO] Falha na compilacao")
        if stderr:
            err_lines = stderr.strip().split('\n')
            print("   Erro (ultimas linhas):")
            for line in err_lines[-10:]:
                print("      " + line[:200])
        return False

    def _build_windows_via_wine(self):
        """Build Windows via Wine"""
        icon = "[W]"
        output_dir = self.build_dir / "windows"
        
        self._kill_wine_processes()
        
        wine = shutil.which("wine64") or shutil.which("wine")
        if not wine:
            print("   " + icon + " [ERRO] Wine nao encontrado")
            return False
        
        if self.wine_python_path and os.path.isfile(self.wine_python_path):
            wine_python = self.wine_python_path
            print("   " + icon + " Python manual: " + wine_python)
        else:
            _, wine_python = self._find_wine_python()
        
        if not wine_python or not os.path.isfile(wine_python):
            print("   " + icon + " [ERRO] Python nao encontrado no Wine")
            self._create_windows_build_script()
            return False
        
        print("   " + icon + " Python: " + wine_python)
        print("   " + icon + " [INSTALL] Instalando dependencias no Wine...")
        
        env = {
            **os.environ,
            "WINEDEBUG": "-all",
            "DISPLAY": ":0",
            "WINEPREFIX": os.path.dirname(os.path.dirname(os.path.dirname(wine_python)))
        }
        
        subprocess.run(
            [wine, wine_python, "-m", "pip", "install", "--quiet", "--no-cache-dir",
             "pyinstaller", "PyQt6", "PyQt6-WebEngine", "pyserial", "cryptography"],
            capture_output=True, text=True, timeout=300, env=env
        )
        
        build_script = self.build_dir / "build_wine.py"
        output_win = "Z:" + str(output_dir).replace("/", "\\")
        source_win = "Z:" + str(self.source_file).replace("/", "\\")
        project_win = "Z:" + str(self.project_root).replace("/", "\\")
        
        script = ('import sys, os\n' +
                 'os.environ["WINEDEBUG"] = "-all"\n' +
                 'sys.path.insert(0, r"' + project_win + '")\n' +
                 '\n' +
                 'import PyInstaller.__main__\n' +
                 'PyInstaller.__main__.run([\n' +
                 '    "--onefile", "--windowed", "--clean", "--noconfirm",\n' +
                 '    "--log-level=WARN",\n' +
                 '    "--name=ArduBlockStudio",\n' +
                 '    "--distpath=" + r"' + output_win + '",\n' +
                 '    "--add-data=" + r"' + project_win + '\\\\extensions;extensions",\n' +
                 '    "--add-data=" + r"' + project_win + '\\\\i18n;i18n",\n' +
                 '    "--add-data=" + r"' + project_win + '\\\\resources;resources",\n' +
                 '    "--hidden-import=PyQt6",\n' +
                 '    "--hidden-import=PyQt6.QtCore",\n' +
                 '    "--hidden-import=PyQt6.QtGui",\n' +
                 '    "--hidden-import=PyQt6.QtWidgets",\n' +
                 '    "--hidden-import=PyQt6.QtWebEngineWidgets",\n' +
                 '    "--hidden-import=PyQt6.QtWebChannel",\n' +
                 '    "--hidden-import=serial",\n' +
                 '    "--hidden-import=cryptography.fernet",\n' +
                 '    "--hidden-import=base64",\n' +
                 '    "--hidden-import=hashlib",\n' +
                 '    "--hidden-import=uuid",\n' +
                 '    "--exclude-module=tkinter",\n' +
                 '    "--exclude-module=unittest",\n' +
                 '    r"' + source_win + '"\n' +
                 '])\n')
        
        build_script.write_text(script)
        
        print("   " + icon + " [BUILD] Compilando (pode demorar 10-30 min)...")
        start = time.time()
        
        try:
            result = subprocess.run(
                [wine, wine_python, str(build_script)],
                capture_output=True, text=True, timeout=1800, env=env
            )
            elapsed = time.time() - start
            
            exe = output_dir / "ArduBlockStudio.exe"
            if exe.exists() and exe.stat().st_size > 5000000:
                self._copy_license_to_build("Windows", output_dir)
                
                size_mb = exe.stat().st_size / (1024*1024)
                print("\n   " + icon + " [OK] SUCESSO! (" + "{:.0f}".format(elapsed) + "s, " + "{:.1f}".format(size_mb) + " MB)")
                self.cache["Windows_" + self.source_hash] = {
                    "path": str(exe), "timestamp": self.timestamp, "size_mb": size_mb
                }
                self._save_cache()
                self._kill_wine_processes()
                return True
            
            print("\n   " + icon + " [ERRO] Falha (" + "{:.0f}".format(elapsed) + "s)")
            if result.stderr:
                print("   Erro: " + result.stderr[:500])
            
            self._kill_wine_processes()
        except subprocess.TimeoutExpired:
            print("\n   " + icon + " [TIMEOUT] Tempo excedido")
            self._kill_wine_processes()
        except Exception as e:
            print("\n   " + icon + " [ERRO] " + str(e))
            self._kill_wine_processes()
        
        return False

    def _find_wine_python(self):
        """Procura Python no Wine"""
        wine = shutil.which("wine64") or shutil.which("wine")
        if not wine:
            return None, None
        
        wine_prefix = os.environ.get("WINEPREFIX", os.path.expanduser("~/.wine"))
        username = os.environ.get("USER", "")
        
        print("   [SEARCH] Procurando Python no Wine...")
        
        base = os.path.join(wine_prefix, "drive_c")
        search_paths = []
        
        for ver in ["310", "311", "312", "39", "38"]:
            ver_dot = ver[0] + "." + ver[1] if len(ver) >= 2 else ver
            
            candidates = [
                os.path.join(base, "Python" + ver_dot, "python.exe"),
                os.path.join(base, "Python" + ver, "python.exe"),
                os.path.join(base, "Program Files", "Python" + ver_dot, "python.exe"),
                os.path.join(base, "Program Files (x86)", "Python" + ver_dot, "python.exe"),
                os.path.join(base, "users", username, "Local Settings", 
                           "Application Data", "Programs", "Python", "Python" + ver_dot, "python.exe"),
                os.path.join(base, "users", username, "AppData", 
                           "Local", "Programs", "Python", "Python" + ver_dot, "python.exe"),
                os.path.join(base, "users", username, "AppData", 
                           "Roaming", "Python", "Python" + ver_dot, "python.exe"),
            ]
            search_paths.extend(candidates)
        
        for path in search_paths:
            if os.path.isfile(path) and os.path.getsize(path) > 10000:
                print("   [FOUND] " + path)
                return wine, path
        
        return wine, None

    def _build_linux_via_wsl(self, output_dir):
        print("   [L] Compilando via WSL...")
        return False

    def _build_linux_via_docker(self, output_dir):
        print("   [L] Compilando via Docker...")
        return False

    def _create_windows_build_script(self):
        script = "@echo off\n" + \
                "chcp 65001 >nul\n" + \
                "echo ========================================\n" + \
                "echo   ArduBlock Studio - Build Windows\n" + \
                "echo ========================================\n" + \
                "pip install pyinstaller PyQt6 PyQt6-WebEngine pyserial cryptography --quiet\n" + \
                "pyinstaller --onefile --windowed --name ArduBlockStudio --clean " + \
                "--add-data \"extensions;extensions\" --add-data \"i18n;i18n\" " + \
                "--add-data \"resources;resources\" --hidden-import=PyQt6.QtCore " + \
                "--hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets " + \
                "--hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel " + \
                "--hidden-import=serial --hidden-import=cryptography.fernet --hidden-import=base64 " + \
                "--hidden-import=hashlib --hidden-import=uuid " + \
                "--exclude-module=tkinter --exclude-module=unittest main.py\n" + \
                "if exist \"dist\\ArduBlockStudio.exe\" (echo [OK] SUCESSO!) else (echo [ERRO] FALHA)\n" + \
                "pause\n"
        p = self.build_dir / "BUILD_WINDOWS.bat"
        p.write_text(script)
        print("   [SCRIPT] Criado: BUILD_WINDOWS.bat")

    def _create_macos_build_script(self):
        script = "#!/bin/bash\n" + \
                "pip3 install pyinstaller PyQt6 PyQt6-WebEngine pyserial cryptography --quiet\n" + \
                "pyinstaller --onefile --windowed --name ArduBlockStudio --clean " + \
                "--add-data \"extensions:extensions\" --add-data \"i18n:i18n\" " + \
                "--add-data \"resources:resources\" --hidden-import=PyQt6.QtCore " + \
                "--hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets " + \
                "--hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel " + \
                "--hidden-import=serial --hidden-import=cryptography.fernet --hidden-import=base64 " + \
                "--hidden-import=hashlib --hidden-import=uuid " + \
                "--exclude-module=tkinter --exclude-module=unittest " + \
                "--osx-bundle-identifier=com.ardublock.studio main.py\n" + \
                "[ -d \"dist/ArduBlockStudio.app\" ] && echo \"[OK] SUCESSO!\" || echo \"[ERRO] FALHA\"\n"
        p = self.build_dir / "build_macos.sh"
        p.write_text(script)
        p.chmod(0o755)
        print("   [SCRIPT] Criado: build_macos.sh")

    def create_package(self, platform_name):
        icon = self.platform_configs[platform_name]["icon"]
        if platform_name == "Windows":
            exe = self.build_dir / "windows" / "ArduBlockStudio.exe"
            if exe.exists() and exe.stat().st_size > 5000000:
                zip_path = self.build_dir / ("ArduBlockStudio-" + self.version + "-windows-x64.zip")
                if not zip_path.exists():
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                        z.write(exe, "ArduBlockStudio.exe")
                        license_file = self.build_dir / "windows" / self.license_filename
                        if license_file.exists():
                            z.write(license_file, self.license_filename)
                print("   " + icon + " [PKG] " + zip_path.name + " (" + "{:.1f}".format(zip_path.stat().st_size/(1024*1024)) + " MB)")
                return True
        elif platform_name == "Linux":
            exe = self.build_dir / "linux" / "ardublock-studio"
            if exe.exists() and exe.stat().st_size > 5000000:
                tar_path = self.build_dir / ("ardublock-studio-" + self.version + "-linux-x64.tar.gz")
                if not tar_path.exists():
                    with tarfile.open(tar_path, "w:gz") as tar:
                        tar.add(exe, "ardublock-studio/ardublock-studio")
                        license_file = self.build_dir / "linux" / self.license_filename
                        if license_file.exists():
                            tar.add(license_file, "ardublock-studio/" + self.license_filename)
                print("   " + icon + " [PKG] " + tar_path.name + " (" + "{:.1f}".format(tar_path.stat().st_size/(1024*1024)) + " MB)")
                return True
        return False

    def print_header(self, targets):
        print("")
        print("=" * 60)
        print("       ARDUBLOCK STUDIO BUILDER v3.6")
        if self.unlimited:
            print("       🔓 MODO SEM LIMITE DE TEMPO 🔓")
        else:
            print("       COM LICENCIAMENTO TEMPORAL")
        print("=" * 60)
        print("")
        print("   Sistema: " + self.current_os + " | Python: " + platform.python_version() + " | Targets: " + ", ".join(targets))
        if self.unlimited:
            print("   🔓 BUILD SEM LIMITE - Licenca PERPETUA")
        elif self.license_duration:
            print("   Licenca: " + self.license_duration)
            print("   Deteccao de 1a execucao: ATIVADA")
            print("   Vinculacao por maquina: ATIVADA")
        print("")


def main():
    parser = argparse.ArgumentParser(description="ArduBlock Studio Builder v3.6")
    parser.add_argument("--linux", action="store_true", help="Build Linux")
    parser.add_argument("--windows", action="store_true", help="Build Windows")
    parser.add_argument("--mac", action="store_true", help="Build macOS")
    parser.add_argument("--all", action="store_true", help="Build todas")
    parser.add_argument("--force", action="store_true", help="Forcar rebuild")
    parser.add_argument("--clean", action="store_true", help="Limpar cache")
    parser.add_argument("--wine-python", type=str, help="Path do python.exe no Wine")
    parser.add_argument("--license", type=str, 
                       help="Duracao da licenca: 1min, 1hour, 1day, 30day, 1month, 360day, 1year")
    parser.add_argument("--unlimited", action="store_true",  # NOVO ARGUMENTO
                       help="Gerar build sem limite de tempo (licenca perpetua)")
    
    args = parser.parse_args()
    
    try:
        import cryptography
    except ImportError:
        print("[INSTALL] Instalando cryptography...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    
    packager = None
    try:
        packager = UniversalPackager(
            wine_python_path=args.wine_python,
            license_duration=args.license,
            unlimited=args.unlimited  # NOVO
        )
        
        if args.clean and packager.cache_dir.exists():
            shutil.rmtree(packager.cache_dir)
            packager.cache_dir.mkdir()
            packager.cache = {}
            print("[CLEAN] Cache limpo\n")
        
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
        print("[PACKAGE] CRIANDO PACOTES")
        print("=" * 60)
        for t in targets:
            plat = t if t != "macOS" else "Darwin"
            packager.create_package(plat)
        
        print("\n" + "=" * 60)
        print("[RESUMO]")
        print("=" * 60)
        for plat, ok in results.items():
            icon = packager.platform_configs[plat if plat != "macOS" else "Darwin"]["icon"]
            status = "[OK]" if ok else "[ERRO]"
            print("   " + icon + " " + plat.ljust(12) + " " + status)
        
        if args.unlimited:
            print("\n   🔓 BUILD SEM LIMITE DE TEMPO")
            print("   🔓 O aplicativo NAO expira")
        elif args.license:
            print("\n   [KEY] Licenca incluida: " + args.license)
            print("   [CAL] Expiracao: " + packager.license_expiration.strftime('%Y-%m-%d %H:%M:%S'))
            print("   [INFO] Funcionalidades ativas:")
            print("      - Deteccao de primeira execucao")
            print("      - Vinculacao de licenca por maquina")
            print("      - Modal de expiracao bilingue")
            print("      - Auto-destruicao apos expiracao")
        
        print("\n   [DIR] " + str(packager.build_dir.absolute()))
        print("=" * 60)
        
        return 0 if all(results.values()) else 1
        
    except KeyboardInterrupt:
        print("\n[STOP] Interrompido pelo usuario")
        subprocess.run(["wineserver", "-k"], capture_output=True)
        return 130
    except Exception as e:
        print("\n[ERRO] " + str(e))
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if packager:
            packager.restore_source()


if __name__ == "__main__":
    sys.exit(main())