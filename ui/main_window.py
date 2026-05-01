"""Main application window."""
import json
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QStatusBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QFont

from core.arduino_cli import ArduinoCLI
from ui.bridge import Bridge
from i18n.translations import Translations


class MainWindow(QMainWindow):
    """Main IDE window."""
    
    def __init__(self, translations: Translations):
        super().__init__()
        self.tr = translations
        self.cli = ArduinoCLI()
        self.bridge = None
        self.channel = None
        self.view = None
        self._setup_ui()
        self._setup_bridge()
        self._load_html()
        
        # Show warning if CLI not found
        if not self.cli.is_available():
            QTimer.singleShot(1500, self._show_cli_warning)
    
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
        
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)
        
        self.bridge.logMsg.connect(self._on_bridge_log)
        # Conectar com flag para evitar loop
        self._language_update_pending = False
        self.bridge.languageChanged.connect(self._on_translations_update)
    
    def _on_translations_update(self, translations_json: str):
        """Update translations in JavaScript without reloading page."""
        if self._language_update_pending:
            return
        
        self._language_update_pending = True
        
        # Execute JavaScript to update translations
        js_code = f"""
        if (typeof updateTranslations === 'function') {{
            updateTranslations({translations_json});
        }}
        """
        self.view.page().runJavaScript(js_code)
        
        # Reset flag after a short delay
        from PyQt6.QtCore import QTimer
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
    
    def closeEvent(self, event):
        """Clean up resources on close."""
        if self.cli:
            self.cli.cleanup()
        event.accept()