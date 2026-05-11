"""Library Manager Dialog for ArduBlock Studio."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QLineEdit,
    QMessageBox, QFileDialog, QProgressBar, QTextEdit,
    QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.library_manager import LibraryManager
from i18n.translations import Translations


class InstallLibraryThread(QThread):
    """Thread for installing libraries without blocking UI."""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, lib_manager, library_name):
        super().__init__()
        self.lib_manager = lib_manager
        self.library_name = library_name
    
    def run(self):
        success, message = self.lib_manager.install_library(self.library_name)
        self.finished.emit(success, message)


class LibraryDialog(QDialog):
    """Dialog for managing Arduino libraries."""
    
    def __init__(self, cli_path: str, translations: Translations, parent=None):
        super().__init__(parent)
        self.cli_path = cli_path
        self.tr = translations
        self.lib_manager = LibraryManager(cli_path)
        self._setup_ui()
        self._load_installed()
        self._load_popular()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Library Manager")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("Arduino Library Manager")
        header.setFont(QFont("Orbitron", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #00d2ff; padding: 10px 0;")
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search libraries...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #162040;
                color: #d8eaff;
                border: 1px solid #00d2ff;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
            }
        """)
        self.search_input.textChanged.connect(self._filter_libraries)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._search_online)
        search_btn.setStyleSheet(self._btn_style())
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1e3058;
                background: #0f1729;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #162040;
                color: #d8eaff;
                padding: 8px 20px;
                border: 1px solid #1e3058;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #1e3058;
                color: #00d2ff;
            }
        """)
        
        # Installed tab
        self.installed_tab = QWidget()
        installed_layout = QVBoxLayout()
        self.installed_list = QListWidget()
        self.installed_list.setStyleSheet(self._list_style())
        installed_layout.addWidget(self.installed_list)
        
        uninstall_btn = QPushButton("Uninstall Selected")
        uninstall_btn.clicked.connect(self._uninstall_library)
        uninstall_btn.setStyleSheet(self._btn_style("#ff4d6d"))
        installed_layout.addWidget(uninstall_btn)
        
        self.installed_tab.setLayout(installed_layout)
        self.tabs.addTab(self.installed_tab, "Installed")
        
        # Popular/Online tab
        self.online_tab = QWidget()
        online_layout = QVBoxLayout()
        self.online_list = QListWidget()
        self.online_list.setStyleSheet(self._list_style())
        online_layout.addWidget(self.online_list)
        
        btn_layout = QHBoxLayout()
        install_btn = QPushButton("Install Selected")
        install_btn.clicked.connect(self._install_library)
        install_btn.setStyleSheet(self._btn_style("#00ff88"))
        btn_layout.addWidget(install_btn)
        
        zip_btn = QPushButton("Install from ZIP")
        zip_btn.clicked.connect(self._install_from_zip)
        zip_btn.setStyleSheet(self._btn_style("#ffb347"))
        btn_layout.addWidget(zip_btn)
        
        online_layout.addLayout(btn_layout)
        self.online_tab.setLayout(online_layout)
        self.tabs.addTab(self.online_tab, "Available")
        
        layout.addWidget(self.tabs)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #5a7aa0; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(self._btn_style())
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1729;
                color: #d8eaff;
            }
        """)
    
    def _btn_style(self, color="#00d2ff"):
        """Get button style."""
        return f"""
            QPushButton {{
                background-color: #162040;
                color: {color};
                border: 1px solid {color};
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1e3058;
            }}
        """
    
    def _list_style(self):
        """Get list widget style."""
        return """
            QListWidget {
                background-color: #0d1117;
                color: #d8eaff;
                border: 1px solid #1e3058;
                border-radius: 5px;
                font-family: 'Fira Code', monospace;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #1e3058;
            }
            QListWidget::item:selected {
                background-color: #1e3058;
                color: #00d2ff;
            }
            QListWidget::item:hover {
                background-color: #162040;
            }
        """
    
    def _load_installed(self):
        """Load installed libraries into the list."""
        self.installed_list.clear()
        libs = self.lib_manager.get_installed_libraries()
        
        if not libs:
            item = QListWidgetItem("No libraries installed")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.installed_list.addItem(item)
            return
        
        for lib in libs:
            text = f"{lib['name']} v{lib['version']}"
            if lib.get('install_path'):
                text += f"\n  Path: {lib['install_path']}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, lib['name'])
            self.installed_list.addItem(item)
    
    def _load_popular(self):
        """Load popular libraries into the list."""
        self.online_list.clear()
        libs = self.lib_manager.get_popular_libraries()
        
        for lib in libs:
            status = "[Installed]" if lib["installed"] else "[Available]"
            text = f"{status} {lib['name']}\n  {lib['description']}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, lib['name'])
            if lib["installed"]:
                item.setForeground(Qt.GlobalColor.gray)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.online_list.addItem(item)
    
    def _filter_libraries(self, text):
        """Filter libraries by search text."""
        for i in range(self.online_list.count()):
            item = self.online_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def _search_online(self):
        """Search for libraries online."""
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.status_label.setText(f"Searching for '{query}'...")
        libs = self.lib_manager.search_libraries(query)
        
        self.online_list.clear()
        if not libs:
            item = QListWidgetItem(f"No results for '{query}'")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.online_list.addItem(item)
        else:
            for lib in libs:
                status = "[Installed]" if lib["installed"] else "[Available]"
                text = f"{status} {lib['name']} v{lib.get('latest_version', '?')}\n  {lib.get('description', '')}"
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, lib['name'])
                self.online_list.addItem(item)
        
        self.status_label.setText(f"Found {len(libs)} results for '{query}'")
        self.tabs.setCurrentWidget(self.online_tab)
    
    def _install_library(self):
        """Install the selected library."""
        current_item = self.online_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Select a library to install")
            return
        
        lib_name = current_item.data(Qt.ItemDataRole.UserRole)
        if not lib_name:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Install",
            f"Install library '{lib_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.status_label.setText(f"Installing {lib_name}...")
        self._install_thread = InstallLibraryThread(self.lib_manager, lib_name)
        self._install_thread.finished.connect(self._on_install_finished)
        self._install_thread.start()
    
    def _on_install_finished(self, success, message):
        """Handle library installation result."""
        if success:
            QMessageBox.information(self, "Success", message)
            self._load_installed()
            self._load_popular()
        else:
            QMessageBox.critical(self, "Error", f"Installation failed:\n{message}")
        self.status_label.setText(message)
    
    def _uninstall_library(self):
        """Uninstall the selected library."""
        current_item = self.installed_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Select a library to uninstall")
            return
        
        lib_name = current_item.data(Qt.ItemDataRole.UserRole)
        if not lib_name:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Uninstall",
            f"Uninstall library '{lib_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        success, message = self.lib_manager.uninstall_library(lib_name)
        if success:
            QMessageBox.information(self, "Success", message)
            self._load_installed()
            self._load_popular()
        else:
            QMessageBox.critical(self, "Error", f"Uninstall failed:\n{message}")
        self.status_label.setText(message)
    
    def _install_from_zip(self):
        """Install a library from a ZIP file."""
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Select Library ZIP File",
            "", "ZIP Files (*.zip);;All Files (*)"
        )
        
        if not zip_path:
            return
        
        success, message = self.lib_manager.install_from_zip(zip_path)
        if success:
            QMessageBox.information(self, "Success", message)
            self._load_installed()
        else:
            QMessageBox.critical(self, "Error", f"ZIP installation failed:\n{message}")
        self.status_label.setText(message)