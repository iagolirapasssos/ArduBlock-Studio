"""Main application window."""
import json
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QStatusBar, QDialog, QVBoxLayout, 
    QListWidget, QPushButton, QFileDialog, QProgressDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from core.arduino_cli import ArduinoCLI
from ui.bridge import Bridge
from i18n.translations import Translations

# Import new components
from core.compilation_cache import get_compilation_cache
from core.project_history import ProjectHistory
from core.error_handler import ErrorHandler

# Import extension system
from extensions.manager import DynamicExtensionManager
from extensions.api import ExtensionAPI


class MainWindow(QMainWindow):
    """Main IDE window."""
    
    def __init__(self, translations: Translations):
        super().__init__()
        self.tr = translations
        self.cli = ArduinoCLI()
        self.bridge = None
        self.channel = None
        self.view = None
        self.ext_api = None
        self.ext_manager = None
        self._extensions_loaded = False
        self._pending_js_queue = []
        
        self._setup_ui()
        self._setup_bridge()
        self._load_html()
        
        # Show warning if CLI not found
        if not self.cli.is_available():
            QTimer.singleShot(1500, self._show_cli_warning)
        
        # Initialize new components
        self.compilation_cache = get_compilation_cache()
        self.project_history = ProjectHistory()
        self.error_handler = ErrorHandler()
        
        # Setup auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # Every 30 seconds
        
        # Setup periodic cache cleanup
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_cache)
        self.cleanup_timer.start(3600000)  # Every hour
        
        # Setup extension system after page loads
        QTimer.singleShot(1500, self._setup_extensions)

    def _auto_save(self):
        """Auto-save current project to history."""
        if self.view:
            self.view.page().runJavaScript("Blockly.Xml.workspaceToDom(workspace);", 
                                           lambda xml: self.project_history.auto_save(xml) if xml else None)
    
    def _cleanup_cache(self):
        """Clean up old compilation cache entries."""
        if hasattr(self.compilation_cache, '_cleanup_old_caches'):
            self.compilation_cache._cleanup_old_caches()
    
    def show_version_history(self):
        """Show version history dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Version History")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Version list
        version_list = QListWidget()
        for v in self.project_history.get_version_list():
            version_list.addItem(f"{v['timestamp'][:19]} - {v['description']} ({v['block_count']} blocks)")
        
        layout.addWidget(version_list)
        
        # Buttons
        restore_btn = QPushButton("Restore Selected Version")
        restore_btn.clicked.connect(lambda: self._restore_version(version_list.currentRow(), dialog))
        layout.addWidget(restore_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def _restore_version(self, index: int, dialog):
        """Restore selected version."""
        versions = self.project_history.get_version_list()
        if 0 <= index < len(versions):
            xml_data = self.project_history.restore_version(versions[index]['id'])
            if xml_data:
                # Escape for JavaScript
                escaped_xml = xml_data.replace('`', '\\`').replace('${', '\\${')
                self.view.page().runJavaScript(f"""
                    if (typeof workspace !== 'undefined') {{
                        workspace.clear();
                        var xml = Blockly.Xml.textToDom(`{escaped_xml}`);
                        Blockly.Xml.domToWorkspace(xml, workspace);
                    }}
                """)
                dialog.accept()

    def add_pdf_export_button(self):
        """Add PDF export button to the toolbar."""
        pass

    def export_to_pdf(self):
        """Export current project to PDF."""
        self.view.page().runJavaScript("getGeneratedCode();", self._on_code_received_for_pdf)
        
    def _on_code_received_for_pdf(self, code):
        """Handle code retrieval for PDF export."""
        if code:
            self.view.page().runJavaScript("Blockly.Xml.workspaceToDom(workspace);", 
                                            lambda xml: self._generate_pdf(xml, code))

    def _generate_pdf(self, xml_dom, code):
        """Generate PDF with both blocks and code."""
        js_code = """
            (function() {
                if (typeof workspace === 'undefined') return JSON.stringify({total_blocks: 0, categories: {}, stats: {digital_pins: 0, analog_pins: 0, variables: 0}});
                const blocks = workspace.getAllBlocks(false);
                const stats = {
                    total_blocks: blocks.length,
                    categories: {},
                    stats: { digital_pins: 0, analog_pins: 0, variables: 0 }
                };
                blocks.forEach(b => {
                    let cat = b.type ? b.type.split('_')[1] || 'Other' : 'Other';
                    stats.categories[cat] = (stats.categories[cat] || 0) + 1;
                    if (b.type && b.type.includes('digital')) stats.stats.digital_pins++;
                    if (b.type && b.type.includes('analog')) stats.stats.analog_pins++;
                    if (b.type && (b.type.includes('var') || b.type.includes('variable'))) stats.stats.variables++;
                });
                return JSON.stringify(stats);
            })()
        """
        self.view.page().runJavaScript(js_code, lambda stats_json: self._do_export_pdf(xml_dom, code, stats_json))

    def _do_export_pdf(self, xml_dom, code, stats_json):
        """Execute PDF export."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to PDF", "",
            "PDF Files (*.pdf);;HTML Files (*.html)"
        )
        
        if not file_path:
            return
        
        progress = QProgressDialog("Generating PDF...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            from core.pdf_exporter import PDFExporter
            exporter = PDFExporter()
            project_name = self.windowTitle().replace(" - ArduBlock Studio", "")
            import json as json_lib
            stats = json_lib.loads(stats_json) if stats_json else {}
            
            pdf_data = exporter.export_project(xml_dom, code, project_name, stats)
            
            if file_path.endswith('.pdf'):
                with open(file_path, 'wb') as f:
                    f.write(pdf_data)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(pdf_data.decode('utf-8'))
            
            exporter.cleanup()
            progress.close()
            
            QMessageBox.information(self, "Export Complete", 
                                    f"Project exported to:\n{file_path}")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Export Failed", str(e))

    def _setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.tr.get('app_title', 'ArduBlock Studio'))
        self.setMinimumSize(1000, 600)
        self.resize(1400, 850)
        
        # Ensure standard window controls
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Create web view
        self.view = QWebEngineView()
        self.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
        self.setCentralWidget(self.view)
        
        # Status bar
        cli_version = self.cli.get_version()
        status_text = f"{self.tr.get('app_title', 'ArduBlock Studio')} | arduino-cli: {cli_version}"
        if self.cli.is_available():
            status_text += f" | {self.tr.get('status_ready', 'Ready')}"
        else:
            status_text += " | arduino-cli not found"
        self.statusBar().showMessage(status_text)
    
    def _setup_bridge(self):
        """Set up the Python-JavaScript bridge."""
        self.bridge = Bridge(self)
        self.bridge.set_cli(self.cli)
        
        # IMPORTANTE: Conecta a janela principal ao bridge para abrir o gerenciador de extensões
        self.bridge.parent_window = self
        
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)
        
        self.bridge.logMsg.connect(self._on_bridge_log)
        self._language_update_pending = False
        self.bridge.languageChanged.connect(self._on_translations_update)
    
    def _on_translations_update(self, translations_json: str):
        """Update translations in JavaScript without reloading page."""
        if self._language_update_pending:
            return
        
        self._language_update_pending = True
        
        js_code = f"""
        if (typeof updateTranslations === 'function') {{
            updateTranslations({translations_json});
        }}
        """
        self.view.page().runJavaScript(js_code)
        
        QTimer.singleShot(500, lambda: setattr(self, '_language_update_pending', False))
        
    def _on_bridge_log(self, message: str):
        """Handle log messages from bridge."""
        print(f"[Bridge] {message}")
    
    def _load_html(self):
        """Load the Blockly HTML interface."""
        from resources.blockly_html import get_blockly_html
        html = get_blockly_html(self.tr)
        self.view.setHtml(html, QUrl("qrc:///"))
    
    def _show_cli_warning(self):
        """Show warning if arduino-cli is not available."""
        msg = QMessageBox(self)
        msg.setWindowTitle("arduino-cli not found")
        msg.setText(
            "<b>The arduino-cli was not detected.</b><br><br>"
            "To compile and upload code to Arduino, install arduino-cli:<br>"
            "<a href='https://arduino.github.io/arduino-cli/latest/installation/'>"
            "https://arduino.github.io/arduino-cli</a><br><br>"
            "You can still create and view your visual programs!"
        )
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()
    
    # ============================================================
    # EXTENSION SYSTEM
    # ============================================================
    
    def _setup_extensions(self):
        """Initialize the extension system after workspace is ready."""
        print("[EXTENSIONS] Initializing extension system...")
        
        # Determina o caminho base (funciona no PyInstaller)
        if getattr(sys, 'frozen', False):
            # Executável compilado
            base_dir = Path(sys._MEIPASS)
        else:
            # Modo desenvolvimento
            base_dir = Path(__file__).parent.parent
        
        # Cria a API e o gerenciador
        self.ext_api = ExtensionAPI(workspace=None, bridge=self.bridge)
        self.ext_api.base_dir = base_dir
        
        # Override inject_js method to use workspace
        self.ext_api.inject_js = self._inject_js_to_workspace
        self.ext_api._inject_js = self._inject_js_to_workspace  # Para compatibilidade
        
        # Create extension manager
        self.ext_manager = DynamicExtensionManager(api=self.ext_api)
        
        # Load all enabled extensions
        self._load_extensions()
    
    def _inject_js_to_workspace(self, js_code: str):
        """Inject JavaScript code into the workspace."""
        if self.view:
            # Queue injection if page not ready
            if not self._extensions_loaded:
                self._pending_js_queue.append(js_code)
            else:
                self.view.page().runJavaScript(js_code)
    
    def _load_extensions(self):
        """Load all enabled extensions."""
        # Check if workspace is ready
        self.view.page().runJavaScript("typeof workspace !== 'undefined'", self._on_workspace_check)
    
    def _on_workspace_check(self, workspace_ready):
        """Callback when workspace readiness is checked."""
        if workspace_ready:
            print("[EXTENSIONS] Workspace ready, loading extensions...")
            
            # Expose API to JavaScript
            self._expose_api_to_javascript()
            
            # Get workspace reference via JavaScript
            self.view.page().runJavaScript("workspace", self._on_workspace_received)
        else:
            # Try again in 500ms
            QTimer.singleShot(500, self._load_extensions)
    
    def _on_workspace_received(self, workspace_ref):
        """Callback when workspace reference is received."""
        # IMPORTANTE: workspace_ref é um proxy JavaScript que referencia workspace
        # Precisamos armazenar isso para a API usar
        if self.ext_api:
            # Em vez de passar self.view.page(), passamos o ID do workspace
            # ou criamos um proxy que pode executar JavaScript no workspace real
            self.ext_api.workspace_id = id(self.view.page())
            
            # Forçar flush de JS pendentes
            self.ext_api.flush()
        
        # Load extensions
        loaded = self.ext_manager.load_all_extensions() if self.ext_manager else []
        print(f"[EXTENSIONS] Loaded {len(loaded)} extensions: {loaded}")
        
        self._extensions_loaded = True
        
        # Process pending JS queue
        for js_code in self._pending_js_queue:
            self.view.page().runJavaScript(js_code)
        self._pending_js_queue.clear()
        
        # Add extension manager button to toolbar
        self._add_extension_button()
    
    def _expose_api_to_javascript(self):
        """Expose extension API to JavaScript."""
        js_code = """
        window.ArduBlockAPI = {
            registerBlock: function(blockDef) {
                if (window.pyBridge && window.pyBridge.registerBlock) {
                    window.pyBridge.registerBlock(JSON.stringify(blockDef));
                }
            },
            registerGenerator: function(blockName, generatorFunc) {
                if (typeof ArduinoGen !== 'undefined') {
                    ArduinoGen.forBlock[blockName] = eval('(' + generatorFunc + ')');
                }
            },
            addCategory: function(name, colour, icon) {
                if (window.dynamicToolbox) {
                    return window.dynamicToolbox.addCategory(name, colour, icon);
                }
                return null;
            },
            addSubcategory: function(parent, name, colour, icon) {
                if (window.dynamicToolbox) {
                    return window.dynamicToolbox.addSubcategory(parent, name, colour, icon);
                }
                return null;
            },
            addBlock: function(category, blockType, subcategory) {
                if (window.dynamicToolbox) {
                    return window.dynamicToolbox.addBlock(category, blockType, subcategory);
                }
                return false;
            },
            addSeparator: function(category) {
                if (window.dynamicToolbox) {
                    return window.dynamicToolbox.addSeparator(category);
                }
                return false;
            },
            getLanguage: function() {
                return window.currentLanguage || 'en';
            },
            log: function(message, type) {
                if (window.log) {
                    window.log(message, type);
                }
                console.log('[' + (type || 'info') + '] ' + message);
            }
        };
        
        if (typeof workspace !== 'undefined' && !window.dynamicToolbox) {
            if (typeof initDynamicToolbox === 'function') {
                initDynamicToolbox(workspace);
            }
        }
        """
        self.view.page().runJavaScript(js_code)
    
    def _add_extension_button(self):
        """Add extension manager button to toolbar."""
        js_code = """
        (function() {
            var header = document.getElementById('header');
            if (!header) return;
            
            var spacer = header.querySelector('.spacer');
            var existingBtn = document.getElementById('extension-manager-btn');
            
            if (!existingBtn) {
                var extBtn = document.createElement('button');
                extBtn.id = 'extension-manager-btn';
                extBtn.className = 'btn btn-serial';
                extBtn.innerHTML = '<span class="material-icons">extension</span> Extensions';
                extBtn.onclick = function() {
                    if (window.pyBridge && window.pyBridge.openExtensionManager) {
                        window.pyBridge.openExtensionManager();
                    }
                };
                
                if (spacer) {
                    spacer.parentNode.insertBefore(extBtn, spacer);
                } else {
                    header.appendChild(extBtn);
                }
            }
        })();
        """
        self.view.page().runJavaScript(js_code)
    
    def open_extension_manager(self):
        """Open extension manager dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QFileDialog, QMessageBox
        from PyQt6.QtGui import QFont
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Extension Manager")
        dialog.setMinimumSize(600, 400)
        dialog.resize(650, 450)
        
        layout = QVBoxLayout()
        
        header = QLabel("🧩 Manage ArduBlock Extensions")
        header.setFont(QFont("Orbitron", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #00d2ff; padding: 10px;")
        layout.addWidget(header)
        
        desc = QLabel("Install extensions to add new blocks, categories, and features to ArduBlock Studio.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #5a7aa0; padding: 0 10px 10px 10px;")
        layout.addWidget(desc)
        
        extensions_list = QListWidget()
        extensions_list.setStyleSheet("""
            QListWidget {
                background-color: #0d1117;
                color: #d8eaff;
                border: 1px solid #1e3058;
                border-radius: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1e3058;
            }
            QListWidget::item:selected {
                background-color: #1e3058;
                color: #00d2ff;
            }
        """)
        
        installed = self.ext_manager.get_installed() if self.ext_manager else []
        
        if not installed:
            extensions_list.addItem("No extensions installed. Click 'Install from ZIP' to add one.")
        else:
            for ext in installed:
                status = "✅" if ext.enabled else "⭕"
                item_text = f"{status}  {ext.name}  v{ext.version}\n    📝 {ext.description[:60]}"
                extensions_list.addItem(item_text)
        
        layout.addWidget(extensions_list)
        
        btn_layout = QHBoxLayout()
        
        install_btn = QPushButton("📦 Install from ZIP")
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #162040;
                color: #00ff88;
                border: 1px solid #00ff88;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e3058;
            }
        """)
        install_btn.clicked.connect(lambda: self._install_extension(dialog, extensions_list))
        btn_layout.addWidget(install_btn)
        
        if installed:
            enable_btn = QPushButton("🔘 Enable/Disable")
            enable_btn.setStyleSheet("""
                QPushButton {
                    background-color: #162040;
                    color: #ffb347;
                    border: 1px solid #ffb347;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e3058;
                }
            """)
            enable_btn.clicked.connect(lambda: self._toggle_extension(extensions_list.currentRow(), dialog, extensions_list))
            btn_layout.addWidget(enable_btn)
            
            uninstall_btn = QPushButton("🗑️ Uninstall")
            uninstall_btn.setStyleSheet("""
                QPushButton {
                    background-color: #162040;
                    color: #ff4d6d;
                    border: 1px solid #ff4d6d;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ff4d6d;
                    color: white;
                }
            """)
            uninstall_btn.clicked.connect(lambda: self._uninstall_extension(extensions_list.currentRow(), dialog, extensions_list))
            btn_layout.addWidget(uninstall_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #162040;
                color: #00d2ff;
                border: 1px solid #00d2ff;
                border-radius: 5px;
                padding: 8px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e3058;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0f1729;
            }
            QLabel {
                color: #d8eaff;
            }
        """)
        dialog.exec()

    def _install_extension(self, parent_dialog, list_widget):
        """Install extension from ZIP file."""
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Select Extension Package",
            "", "ArduBlock Extension (*.absx *.zip);;All Files (*)"
        )
        
        if zip_path and self.ext_manager:
            from pathlib import Path
            success = self.ext_manager.install_from_zip(Path(zip_path))
            
            if success:
                QMessageBox.information(self, "Success", "Extension installed successfully!\nRestart may be required for changes to take effect.")
                parent_dialog.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to install extension.\nMake sure the package contains a valid manifest.json file.")

    def _toggle_extension(self, index, parent_dialog, list_widget):
        """Enable or disable an extension."""
        if not self.ext_manager:
            return
        
        installed = self.ext_manager.get_installed()
        if 0 <= index < len(installed):
            ext = installed[index]
            if ext.enabled:
                self.ext_manager.disable(ext.id)
                QMessageBox.information(self, "Success", f"Extension '{ext.name}' disabled.\nRestart to apply changes.")
            else:
                self.ext_manager.enable(ext.id)
                QMessageBox.information(self, "Success", f"Extension '{ext.name}' enabled.\nRestart to apply changes.")
            
            parent_dialog.accept()

    def _uninstall_extension(self, index, parent_dialog, list_widget):
        """Uninstall an extension."""
        if not self.ext_manager:
            return
        
        installed = self.ext_manager.get_installed()
        if 0 <= index < len(installed):
            ext = installed[index]
            
            reply = QMessageBox.question(
                self, "Confirm Uninstall",
                f"Uninstall extension '{ext.name}'?\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.ext_manager.uninstall(ext.id)
                QMessageBox.information(self, "Success", f"Extension '{ext.name}' uninstalled!")
                parent_dialog.accept()
    
    def closeEvent(self, event):
        """Clean up resources on close."""
        if self.cli:
            self.cli.cleanup()
        if hasattr(self, 'compilation_cache'):
            self.compilation_cache.shutdown()
        event.accept()