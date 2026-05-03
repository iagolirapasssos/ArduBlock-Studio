"""Python-JavaScript bridge for Blockly communication."""
import json
import threading
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from core.arduino_cli import ArduinoCLI
from core.boards import BOARDS_DATABASE
from config.permissions import PermissionManager
from i18n.translations import Translations

# Import extension system (corrigido)
try:
    from extensions.manager import DynamicExtensionManager
except ImportError:
    DynamicExtensionManager = None
    print("[WARN] Extension system not available")

try:
    from extensions.api import ExtensionAPI
except ImportError:
    ExtensionAPI = None
    print("[WARN] Extension API not available")


class Bridge(QObject):
    """Bridge between Python backend and JavaScript frontend."""
    
    # Signals to JavaScript
    boardsDetected = pyqtSignal(str)
    compileResult = pyqtSignal(str)
    uploadResult = pyqtSignal(str)
    logMsg = pyqtSignal(str)
    languageChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cli = None
        self.perm_manager = PermissionManager()
        self._serial_monitors = []
        self.tr = Translations()
        self._current_language = "en"
        self.parent_window = parent
        
        # Initialize extension system
        self.ext_manager = None
        self.ext_api = None
        self._init_extensions()
    
    def _init_extensions(self):
        """Initialize extension system."""
        if DynamicExtensionManager and ExtensionAPI:
            try:
                self.ext_api = ExtensionAPI(workspace=None, bridge=self)
                self.ext_manager = DynamicExtensionManager(api=self.ext_api)
                print("[EXTENSIONS] Extension system initialized")
            except Exception as e:
                print(f"[EXTENSIONS] Failed to initialize: {e}")
    
    def set_cli(self, cli: ArduinoCLI):
        """Set the ArduinoCLI instance after initialization."""
        self.cli = cli
    
    @pyqtSlot(str)
    def setProgrammer(self, programmer_id: str):
        """Set the programmer for upload."""
        if self.cli:
            self.cli.set_programmer(programmer_id)
            self.logMsg.emit(f"[PROG] Programmer set to: {programmer_id or 'Default'}")

    @pyqtSlot(result=str)
    def getProgrammers(self) -> str:
        """Get list of available programmers."""
        if self.cli:
            return json.dumps(self.cli.get_programmers())
        return json.dumps([])

    @pyqtSlot(str, str, str, str)
    def upload(self, code: str, fqbn: str, port: str, programmer: str = ""):
        """Upload code to Arduino board with optional programmer."""
        if not self.cli:
            self.logMsg.emit("[ERROR] ArduinoCLI not initialized")
            return
            
        def _run():
            self.logMsg.emit("[UPLOAD] Sending to board...")
            self.perm_manager.grant_port_permissions(port)
            ok, msg = self.cli.upload(code, fqbn, port, programmer)
            self.uploadResult.emit(json.dumps({"ok": ok, "msg": msg}))
        
        threading.Thread(target=_run, daemon=True).start()
    
    @pyqtSlot(str)
    def injectJavaScript(self, js_code: str):
        """Inject JavaScript code into the workspace."""
        if self.parent_window and hasattr(self.parent_window, 'view'):
            self.parent_window.view.page().runJavaScript(js_code)
        
    @pyqtSlot()
    def openLibraryManager(self):
        """Open the library manager dialog."""
        if not self.cli or not self.cli.is_available():
            self.logMsg.emit("[LIB] arduino-cli required for Library Manager")
            QMessageBox.warning(
                None, "Library Manager",
                "arduino-cli is required for Library Manager.\n"
                "Please install from: https://arduino.github.io/arduino-cli"
            )
            return
        
        try:
            from ui.library_dialog import LibraryDialog
            dialog = LibraryDialog(self.cli.cli_path, self.tr, None)
            dialog.exec()
            self.logMsg.emit("[LIB] Library Manager closed")
        except Exception as e:
            self.logMsg.emit(f"[LIB] Error: {e}")

    @pyqtSlot()
    def openExtensionManager(self):
        """Open extension manager dialog."""
        if self.parent_window and hasattr(self.parent_window, 'open_extension_manager'):
            self.parent_window.open_extension_manager()
        else:
            self.logMsg.emit("[EXTENSIONS] Cannot open manager - window not available")

    @pyqtSlot(str)
    def registerBlock(self, block_def_json: str):
        """Register a new block from extension."""
        try:
            block_def = json.loads(block_def_json)
            if self.ext_api:
                # TODO: Implement block registration
                self.logMsg.emit(f"[EXTENSIONS] Registering block: {block_def.get('name', 'unknown')}")
        except Exception as e:
            self.logMsg.emit(f"[EXTENSIONS] Error registering block: {e}")

    @pyqtSlot(str)
    def setLanguage(self, lang: str):
        """Change the application language."""
        print(f"[Bridge] Changing language to: {lang}")
        self._current_language = lang
        self.tr.language = lang
        
        # Get all translations for current language
        translations = self.tr.get_all()
        translations_json = json.dumps(translations)
        
        print(f"[Bridge] Sending translations: {list(translations.keys())[:5]}...")
        
        # Send updated translations to JavaScript
        self.languageChanged.emit(translations_json)
        self.logMsg.emit(f"[LANG] Language changed to: {lang.upper()}")

    @pyqtSlot(result=str)
    def getLanguage(self) -> str:
        """Get current language."""
        return self.tr.language

    @pyqtSlot(result=str)
    def getTranslations(self) -> str:
        """Get all translations for current language as JSON."""
        return json.dumps(self.tr.get_all())
        
    @pyqtSlot()
    def detectBoards(self):
        """Detect connected Arduino boards."""
        if not self.cli:
            self.logMsg.emit("[ERROR] ArduinoCLI not initialized")
            return
            
        def _run():
            self.logMsg.emit("[BOARDS] Scanning serial ports...")
            boards = self.cli.detect_boards()
            if not boards:
                self.logMsg.emit("[BOARDS] No ports found. Check USB cable.")
            self.boardsDetected.emit(json.dumps(boards))
        
        threading.Thread(target=_run, daemon=True).start()
    
    @pyqtSlot(str, str)
    def compile(self, code: str, fqbn: str):
        """Compile Arduino code."""
        if not self.cli:
            self.logMsg.emit("[ERROR] ArduinoCLI not initialized")
            return
            
        def _run():
            self.logMsg.emit("[COMPILE] Compiling...")
            ok, msg = self.cli.compile(code, fqbn)
            self.compileResult.emit(json.dumps({"ok": ok, "msg": msg}))
        
        threading.Thread(target=_run, daemon=True).start()
    
    @pyqtSlot(str, str, str)
    def upload(self, code: str, fqbn: str, port: str):
        """Upload code to Arduino board."""
        if not self.cli:
            self.logMsg.emit("[ERROR] ArduinoCLI not initialized")
            return
            
        def _run():
            self.logMsg.emit("[UPLOAD] Sending to board...")
            self.perm_manager.grant_port_permissions(port)
            ok, msg = self.cli.upload(code, fqbn, port)
            self.uploadResult.emit(json.dumps({"ok": ok, "msg": msg}))
        
        threading.Thread(target=_run, daemon=True).start()
    
    @pyqtSlot(result=str)
    def getAllBoards(self) -> str:
        """Get list of all supported boards."""
        return json.dumps(BOARDS_DATABASE)
    
    @pyqtSlot(result=str)
    def getCLIVersion(self) -> str:
        """Get arduino-cli version."""
        if self.cli:
            return self.cli.get_version()
        return "Not installed"
    
    @pyqtSlot(str)
    def saveWorkspace(self, xml: str):
        """Save workspace to file."""
        try:
            fname, _ = QFileDialog.getSaveFileName(
                None, "Save Project", str(Path.home()),
                "ArduBlock Studio (*.abs);;XML (*.xml)"
            )
            if fname:
                if not fname.endswith((".abs", ".xml")):
                    fname += ".abs"
                Path(fname).write_text(xml, encoding="utf-8")
                self.logMsg.emit(f"[SAVE] Saved: {fname}")
        except Exception as e:
            self.logMsg.emit(f"[ERROR] Save failed: {str(e)}")
    
    @pyqtSlot(result=str)
    def loadWorkspace(self) -> str:
        """Load workspace from file."""
        try:
            fname, _ = QFileDialog.getOpenFileName(
                None, "Open Project", str(Path.home()),
                "ArduBlock Studio (*.abs);;XML (*.xml);;All (*)"
            )
            if fname:
                return Path(fname).read_text(encoding="utf-8")
        except Exception as e:
            self.logMsg.emit(f"[ERROR] Load failed: {str(e)}")
        return ""
    
    @pyqtSlot(str)
    def openSerial(self, port: str):
        """Open serial monitor dialog."""
        if not self.cli or not self.cli.is_available():
            self.logMsg.emit("[SERIAL] arduino-cli required for Serial Monitor")
            QMessageBox.warning(
                None, "Serial Monitor",
                "arduino-cli is required for Serial Monitor.\n"
                "Please install from: https://arduino.github.io/arduino-cli"
            )
            return
        
        self.perm_manager.grant_port_permissions(port)
        
        try:
            from ui.serial_monitor import SerialMonitorWidget
            monitor = SerialMonitorWidget(
                self.cli.cli_path,
                port,
                self.tr
            )
            
            monitor.setWindowFlags(
                monitor.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
            )
            
            self._serial_monitors.append(monitor)
            monitor.show()
            self.logMsg.emit(f"[SERIAL] Serial Monitor opened for {port}")
            
        except Exception as e:
            self.logMsg.emit(f"[SERIAL] Error: {e}")