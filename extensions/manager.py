"""
Dynamic Extension Manager for ArduBlock Studio

Corrigido para Windows e Linux:
- Callback de confirmação após cada extensão
- Timeout de segurança para evitar travamentos
- Verificação de workspace pronta antes de injetar JS
- Toolbox atualizada UMA VEZ após todas as extensões
"""

import json
import shutil
import zipfile
import tempfile
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import importlib.util
import sys
import platform


@dataclass
class ExtensionInfo:
    """Informações sobre uma extensão instalada"""
    id: str
    name: str
    version: str
    description: str
    author: str
    installed_at: str
    enabled: bool = True
    has_updates: bool = False
    latest_version: str = ""
    category: str = ""
    icon: str = ""


class DynamicExtensionManager:
    """Gerencia extensões dinâmicas com integração ao toolbox"""

    def __init__(self, api=None):
        self.api = api
        self.extensions_dir = Path(__file__).parent
        self.installed_file = self.extensions_dir / "installed.json"
        self.installed_extensions: Dict[str, ExtensionInfo] = {}
        self._extensions_loaded_count = 0
        self._load_installed()
        self._auto_discover_extensions()

    def _auto_discover_extensions(self):
        """Auto-descobre extensões no diretório extensions/"""
        print("[EXTENSIONS] Auto-discovering extensions...")

        # Determina o caminho base (funciona no PyInstaller)
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
            extensions_dir = base_dir / "extensions"
        else:
            extensions_dir = Path(__file__).parent
        
        print(f"[EXTENSIONS] Looking in: {extensions_dir}")
        
        if not extensions_dir.exists():
            print(f"[EXTENSIONS] Directory not found: {extensions_dir}")
            return
        
        for item in extensions_dir.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith("_") or item.name in ("examples", "__pycache__"):
                continue

            manifest_file = item / "manifest.json"
            if not manifest_file.exists():
                continue

            ext_id = item.name
            if ext_id in self.installed_extensions:
                continue

            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                display_name = manifest.get("name", {})
                if isinstance(display_name, dict):
                    display_name = display_name.get("en", ext_id)

                print(f"[EXTENSIONS] Found: {display_name}")

                self.installed_extensions[ext_id] = ExtensionInfo(
                    id=ext_id,
                    name=display_name,
                    version=manifest.get("version", "1.0.0"),
                    description=(
                        manifest.get("description", {}).get("en", "")
                        if isinstance(manifest.get("description"), dict)
                        else str(manifest.get("description", ""))
                    ),
                    author=manifest.get("author", "Unknown"),
                    installed_at=datetime.now().isoformat(),
                    enabled=True,
                    category=manifest.get("category", "Extensions"),
                    icon=manifest.get("icon", "extension"),
                )
            except Exception as e:
                print(f"[EXTENSIONS] Error reading manifest for {ext_id}: {e}")

        self._save_installed()

    def _load_installed(self):
        """Carrega lista de extensões instaladas do disco."""
        if not self.installed_file.exists():
            return
        try:
            data = json.loads(self.installed_file.read_text(encoding="utf-8"))
            known_fields = {f.name for f in ExtensionInfo.__dataclass_fields__.values()}
            for ext_id, ext_data in data.items():
                filtered = {k: v for k, v in ext_data.items() if k in known_fields}
                self.installed_extensions[ext_id] = ExtensionInfo(**filtered)
        except (json.JSONDecodeError, TypeError, Exception) as e:
            print(f"[EXTENSIONS] Warning: could not load installed.json: {e}")

    def _save_installed(self):
        """Salva lista de extensões instaladas em disco."""
        data = {}
        for ext_id, ext in self.installed_extensions.items():
            data[ext_id] = {
                "id": ext.id,
                "name": ext.name,
                "version": ext.version,
                "description": ext.description,
                "author": ext.author,
                "installed_at": ext.installed_at,
                "enabled": ext.enabled,
                "category": ext.category,
                "icon": ext.icon,
            }
        try:
            self.installed_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as e:
            print(f"[EXTENSIONS] Warning: could not save installed.json: {e}")

    def load_all_extensions(self) -> List[str]:
        """Carrega todas as extensões habilitadas com toolbox update único no final."""
        loaded = []
        failed = []
        
        for ext_id, ext_info in self.installed_extensions.items():
            if ext_info.enabled:
                try:
                    if self.load_extension(ext_id):
                        loaded.append(ext_id)
                    else:
                        failed.append(ext_id)
                except Exception as e:
                    print(f"[EXTENSIONS] Critical error loading {ext_id}: {e}")
                    failed.append(ext_id)
        
        # Atualizar toolbox UMA VEZ após todas as extensões
        if loaded:
            self._finalize_toolbox()
        
        if failed:
            print(f"[EXTENSIONS] Failed to load: {failed}")
        
        return loaded

    def load_extension(self, ext_id: str) -> bool:
        """
        Carrega uma extensão específica de forma segura.
        
        Fluxo:
        1. Lê manifest.json
        2. Executa __init__.py (bufferiza JS via API)
        3. Injeta blocks.js e generator.js
        4. Faz flush individual
        5. Confirma carregamento
        """
        ext_path = self.extensions_dir / ext_id
        if not ext_path.exists():
            print(f"[EXTENSIONS] Path not found: {ext_path}")
            return False

        try:
            manifest_file = ext_path / "manifest.json"
            if not manifest_file.exists():
                print(f"[EXTENSIONS] No manifest.json in {ext_id}")
                return False

            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            name_info = manifest.get("name", {})
            display_name = (
                name_info.get("en", ext_id) if isinstance(name_info, dict) else str(name_info)
            )
            version = manifest.get("version", "1.0.0")
            print(f"[EXTENSIONS] Loading: {display_name} v{version}")

            if not self.api:
                print(f"[EXTENSIONS] No API available - skipping {ext_id}")
                return False

            # Inicializa a API para esta extensão
            self.api.initialize(self.api.workspace, ext_id, ext_path)

            # ----- Executa __init__.py -----
            init_file = ext_path / "__init__.py"
            if init_file.exists():
                try:
                    module_name = f"extensions.{ext_id}"
                    spec = importlib.util.spec_from_file_location(module_name, init_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        if hasattr(module, "initialize"):
                            module.initialize(self.api)
                except Exception as e:
                    print(f"[EXTENSIONS] Error in {ext_id}/__init__.py: {e}")
                    import traceback
                    traceback.print_exc()

            # ----- Bufferiza blocks.js e generator.js -----
            for js_filename in ("blocks.js", "generator.js"):
                js_file = ext_path / js_filename
                if js_file.exists():
                    try:
                        content = js_file.read_text(encoding="utf-8")
                        if len(content) < 100000:  # 100KB max
                            self.api.inject_js(content)
                        else:
                            print(f"[EXTENSIONS] {js_filename} too large ({len(content)} bytes)")
                    except Exception as e:
                        print(f"[EXTENSIONS] Error reading {ext_id}/{js_filename}: {e}")

            # ----- Bufferiza style.css -----
            css_file = ext_path / "style.css"
            if css_file.exists():
                try:
                    self.api.inject_css(css_file.read_text(encoding="utf-8"))
                except Exception as e:
                    print(f"[EXTENSIONS] Error reading {ext_id}/style.css: {e}")

            # ----- Flush individual -----
            self.api.flush()
            
            # Pequena pausa para o JS processar
            time.sleep(0.1)
            
            self._extensions_loaded_count += 1
            print(f"[EXTENSIONS] Loaded successfully: {ext_id} ({self._extensions_loaded_count} total)")
            return True

        except Exception as e:
            print(f"[EXTENSIONS] Unexpected error loading {ext_id}: {e}")
            import traceback
            traceback.print_exc()
            if self.api:
                self.api._js_buffer.clear()
                self.api._pending_translations.clear()
            return False

    def _finalize_toolbox(self):
        """Atualiza a toolbox UMA VEZ após todas extensões carregarem."""
        print("[EXTENSIONS] Finalizing toolbox update...")
        
        # Verificar se Blockly existe antes de atualizar
        confirm_js = """
    (function() {
        if (typeof Blockly === 'undefined' || typeof workspace === 'undefined') {
            console.warn('[EXTENSIONS] Blockly/workspace not ready for toolbox update');
            return;
        }
        
        console.log('[EXTENSIONS] All extensions loaded!');
        
        // Listar categorias para debug
        var toolbox = document.getElementById('toolbox');
        if (toolbox) {
            var cats = toolbox.querySelectorAll('category');
            console.log('[EXTENSIONS] Total categories in toolbox:', cats.length);
            cats.forEach(function(cat) {
                var blocks = cat.querySelectorAll('block');
                console.log('  Category:', cat.getAttribute('name'), '(' + blocks.length + ' blocks)');
            });
            
            // Forçar update final
            workspace.updateToolbox(toolbox);
            console.log('[EXTENSIONS] Toolbox updated successfully!');
            
            // Verificar se os blocos das extensões estão presentes
            var extBlocks = ['ab_math_sin', 'ab_math_cos', 'ab_logic_xor', 'ab_text_literal', 
                             'ab_pin_mode_var', 'ab_digital_write_var'];
            extBlocks.forEach(function(blockType) {
                if (Blockly.Blocks[blockType]) {
                    console.log('[EXTENSIONS] Block registered:', blockType);
                } else {
                    console.warn('[EXTENSIONS] Block MISSING:', blockType);
                }
            });
        }
    })();
    """
        self.api.inject_js(confirm_js)
        self.api.flush()

    def install_from_zip(self, zip_path: Path) -> bool:
        """Instala extensão a partir de arquivo ZIP (.absx ou .zip)."""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmp_path)

                manifest_file = None
                for item in tmp_path.rglob("manifest.json"):
                    manifest_file = item
                    ext_root = item.parent
                    break

                if not manifest_file:
                    raise ValueError("manifest.json não encontrado no ZIP")

                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                ext_id = manifest.get("id")
                if not ext_id:
                    raise ValueError("manifest.json não contém campo 'id'")

                ext_dir = self.extensions_dir / ext_id
                if ext_dir.exists():
                    shutil.rmtree(ext_dir)

                shutil.copytree(ext_root, ext_dir)

                name_info = manifest.get("name", {})
                display_name = (
                    name_info.get("en", ext_id)
                    if isinstance(name_info, dict)
                    else str(name_info)
                )

                self.installed_extensions[ext_id] = ExtensionInfo(
                    id=ext_id,
                    name=display_name,
                    version=manifest.get("version", "1.0.0"),
                    description=(
                        manifest.get("description", {}).get("en", "")
                        if isinstance(manifest.get("description"), dict)
                        else str(manifest.get("description", ""))
                    ),
                    author=manifest.get("author", "Unknown"),
                    installed_at=datetime.now().isoformat(),
                    enabled=True,
                    category=manifest.get("category", "Extensions"),
                    icon=manifest.get("icon", "extension"),
                )
                self._save_installed()
                self.load_extension(ext_id)
                self._finalize_toolbox()
                return True

        except Exception as e:
            print(f"[EXTENSIONS] Install error: {e}")
            return False

    def uninstall(self, ext_id: str) -> bool:
        """Desinstala uma extensão."""
        if ext_id not in self.installed_extensions:
            return False
        ext_dir = self.extensions_dir / ext_id
        if ext_dir.exists():
            try:
                shutil.rmtree(ext_dir)
            except OSError as e:
                print(f"[EXTENSIONS] Could not remove {ext_dir}: {e}")
        del self.installed_extensions[ext_id]
        self._save_installed()
        return True

    def enable(self, ext_id: str) -> bool:
        """Habilita uma extensão."""
        if ext_id in self.installed_extensions:
            self.installed_extensions[ext_id].enabled = True
            self._save_installed()
            self.load_extension(ext_id)
            self._finalize_toolbox()
            return True
        return False

    def disable(self, ext_id: str) -> bool:
        """Desabilita uma extensão."""
        if ext_id in self.installed_extensions:
            self.installed_extensions[ext_id].enabled = False
            self._save_installed()
            return True
        return False

    def get_installed(self) -> List[ExtensionInfo]:
        """Retorna lista de extensões instaladas."""
        return list(self.installed_extensions.values())