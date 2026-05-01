"""Serial monitor widget for ArduBlock Studio."""
import subprocess
import threading
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from i18n.translations import Translations

class SerialMonitorWidget(QDialog):
    """Serial monitor dialog for communication with Arduino."""
    
    # Google Material Icons (using unicode escapes for cross-platform compatibility)
    ICON_CLEAR = "\u26f6"      # refresh
    ICON_PAUSE = "\u23f8"      # pause
    ICON_PLAY = "\u25b6"       # play
    ICON_SEND = "\u2b06"       # upload
    ICON_CLOSE = "\u2715"      # close
    ICON_CONNECTED = "\u26ab"  # circle
    ICON_DISCONNECTED = "\u26aa"  # empty circle
    
    def __init__(self, cli_path: str, port: str, translations: Translations, parent=None):
        super().__init__(parent)
        self.cli_path = cli_path
        self.port = port
        self.tr = translations
        self.serial_process = None
        self.reader_thread = None
        self._setup_ui()
        self.start_monitor()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{self.tr.get('monitor_title')} - {self.port}")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls bar
        controls_layout = QHBoxLayout()
        
        # Baud rate selector
        controls_layout.addWidget(QLabel(self.tr.get('monitor_baud_label')))
        self.baud_selector = QComboBox()
        self.baud_selector.addItems([
            "300", "1200", "2400", "4800", "9600",
            "19200", "38400", "57600", "74880",
            "115200", "230400", "250000", "500000",
            "1000000", "2000000"
        ])
        self.baud_selector.setCurrentText("9600")
        self.baud_selector.currentTextChanged.connect(self.change_baud_rate)
        controls_layout.addWidget(self.baud_selector)
        
        controls_layout.addStretch()
        
        # Control buttons
        clear_btn = QPushButton(f"{self.ICON_CLEAR} {self.tr.get('monitor_clear')}")
        clear_btn.clicked.connect(lambda: self.output_text.clear())
        controls_layout.addWidget(clear_btn)
        
        self.pause_btn = QPushButton(f"{self.ICON_PAUSE} {self.tr.get('monitor_pause')}")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        controls_layout.addWidget(self.pause_btn)
        
        # Send controls
        controls_layout.addWidget(QLabel(f"{self.ICON_SEND}:"))
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Type to send...")
        self.send_input.returnPressed.connect(self.send_data)
        controls_layout.addWidget(self.send_input)
        
        send_btn = QPushButton(self.tr.get('monitor_send'))
        send_btn.clicked.connect(self.send_data)
        controls_layout.addWidget(send_btn)
        
        layout.addLayout(controls_layout)
        
        # Output area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        self._apply_output_style()
        layout.addWidget(self.output_text)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel(f"{self.ICON_CONNECTED} Connected to {self.port} @ 9600 baud")
        self.status_label.setStyleSheet("color: #00d2ff; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        close_btn = QPushButton(f"{self.ICON_CLOSE} {self.tr.get('monitor_close')}")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d6d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff3355;
            }
        """)
        status_layout.addWidget(close_btn)
        
        layout.addLayout(status_layout)
        self.setLayout(layout)
        self._apply_window_style()
    
    def _apply_output_style(self):
        """Apply styling to output text area."""
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #00ff88;
                border: 2px solid #1e3058;
                border-radius: 8px;
                padding: 10px;
            }
        """)
    
    def _apply_window_style(self):
        """Apply styling to the dialog window."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1729;
                color: #d8eaff;
                font-family: 'Nunito', sans-serif;
            }
            QLabel {
                color: #d8eaff;
                font-weight: bold;
            }
            QComboBox {
                background-color: #162040;
                color: #d8eaff;
                border: 1px solid #00d2ff;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 100px;
            }
            QPushButton {
                background-color: #162040;
                color: #00d2ff;
                border: 1px solid #00d2ff;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e3058;
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton:checked {
                background-color: #ffb347;
                color: #0f1729;
            }
            QLineEdit {
                background-color: #162040;
                color: #d8eaff;
                border: 1px solid #00d2ff;
                border-radius: 5px;
                padding: 5px 10px;
                font-family: 'Courier New', monospace;
            }
        """)
    
    def start_monitor(self):
        """Start the serial monitor process."""
        try:
            baud = self.baud_selector.currentText()
            cmd = [self.cli_path, "monitor", "-p", self.port, "--config", f"serial.baudrate={baud}"]
            
            self.serial_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.reader_thread = threading.Thread(target=self._read_serial_output, daemon=True)
            self.reader_thread.start()
            
        except Exception as e:
            self.output_text.append(f"Error starting monitor: {str(e)}")
    
    def _read_serial_output(self):
        """Read serial output in a separate thread."""
        while self.serial_process and not self.serial_process.poll():
            if self.pause_btn.isChecked():
                time.sleep(0.1)
                continue
            
            try:
                line = self.serial_process.stdout.readline()
                if line:
                    QTimer.singleShot(0, lambda l=line: self._append_output(l))
            except (IOError, OSError):
                break
        
        if self.serial_process:
            QTimer.singleShot(0, lambda: self.status_label.setText(
                f"{self.ICON_DISCONNECTED} Disconnected from {self.port}"
            ))
    
    def _append_output(self, text: str):
        """Append text to output area."""
        clean_text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.output_text.insertPlainText(clean_text)
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_data(self):
        """Send data to serial port."""
        if not self.serial_process or self.serial_process.poll() is not None:
            QMessageBox.warning(self, "Error", "Serial monitor is not connected!")
            return
        
        data = self.send_input.text()
        if data:
            try:
                if not data.endswith('\n'):
                    data += '\n'
                
                self.serial_process.stdin.write(data)
                self.serial_process.stdin.flush()
                
                self.output_text.insertPlainText(f"\n{self.ICON_SEND} Sent: {data}")
                self.send_input.clear()
                
            except (IOError, OSError) as e:
                QMessageBox.warning(self, "Error", f"Error sending data: {str(e)}")
    
    def change_baud_rate(self, new_baud: str):
        """Change the baud rate."""
        if self.serial_process:
            self.serial_process.terminate()
            try:
                self.serial_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.serial_process.kill()
            
            self.output_text.clear()
            self.start_monitor()
            self.status_label.setText(f"{self.ICON_CONNECTED} Connected to {self.port} @ {new_baud} baud")
    
    def toggle_pause(self, paused: bool):
        """Toggle pause/resume of monitor output."""
        if paused:
            self.pause_btn.setText(f"{self.ICON_PLAY} {self.tr.get('monitor_resume')}")
        else:
            self.pause_btn.setText(f"{self.ICON_PAUSE} {self.tr.get('monitor_pause')}")
    
    def closeEvent(self, event):
        """Clean up resources on close."""
        if self.serial_process:
            self.serial_process.terminate()
            try:
                self.serial_process.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                self.serial_process.kill()
        
        event.accept()