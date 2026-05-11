"""Serial monitor widget for ArduBlock Studio."""
import threading
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from i18n.translations import Translations

# Usar pyserial diretamente em vez de arduino-cli
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("AVISO: pyserial nao encontrado. Instale com: pip install pyserial")


class SerialMonitorWidget(QDialog):
    """Serial monitor dialog for communication with Arduino."""
    
    # Sinais para comunicacao thread-safe
    data_received = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)
    
    # Icons
    ICON_CLEAR = "🗑️"
    ICON_PAUSE = "⏸️"
    ICON_PLAY = "▶️"
    ICON_SEND = "⬆️"
    ICON_CLOSE = "✕"
    ICON_CONNECTED = "🟢"
    ICON_DISCONNECTED = "⚪"
    
    def __init__(self, cli_path: str, port: str, translations: Translations, parent=None):
        super().__init__(parent)
        self.cli_path = cli_path
        self.port = port
        self.tr = translations
        self.serial_conn = None
        self.reader_thread = None
        self.running = False
        self.paused = False
        
        # Conectar sinais
        self.data_received.connect(self._append_output)
        self.connection_changed.connect(self._update_status)
        
        self._setup_ui()
        self.start_monitor()
    
    def _setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{self.tr.get('monitor_title', 'Serial Monitor')} - {self.port}")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls bar
        controls_layout = QHBoxLayout()
        
        # Baud rate selector
        controls_layout.addWidget(QLabel(self.tr.get('monitor_baud_label', 'Baud:')))
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
        
        # Line ending selector
        controls_layout.addWidget(QLabel("End:"))
        self.line_ending = QComboBox()
        self.line_ending.addItems(["None", "Newline (\\n)", "Carriage Return (\\r)", "Both (\\r\\n)"])
        self.line_ending.setCurrentText("Newline (\\n)")
        controls_layout.addWidget(self.line_ending)
        
        controls_layout.addStretch()
        
        # Control buttons
        clear_btn = QPushButton(f"{self.ICON_CLEAR} {self.tr.get('monitor_clear', 'Clear')}")
        clear_btn.clicked.connect(lambda: self.output_text.clear())
        controls_layout.addWidget(clear_btn)
        
        self.pause_btn = QPushButton(f"{self.ICON_PAUSE} {self.tr.get('monitor_pause', 'Pause')}")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self.toggle_pause)
        controls_layout.addWidget(self.pause_btn)
        
        # Send controls
        controls_layout.addWidget(QLabel(f"{self.ICON_SEND}:"))
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Type to send...")
        self.send_input.returnPressed.connect(self.send_data)
        controls_layout.addWidget(self.send_input)
        
        send_btn = QPushButton(self.tr.get('monitor_send', 'Send'))
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
        
        close_btn = QPushButton(f"{self.ICON_CLOSE} {self.tr.get('monitor_close', 'Close')}")
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
        """Start the serial monitor using pyserial."""
        if not SERIAL_AVAILABLE:
            self.output_text.append("ERROR: pyserial not installed!")
            self.status_label.setText(f"{self.ICON_DISCONNECTED} pyserial not available")
            return
        
        try:
            baud = int(self.baud_selector.currentText())
            
            # Fechar conexao existente
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            
            # Abrir porta serial
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=baud,
                timeout=0.1,
                write_timeout=1
            )
            
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_serial_data, daemon=True)
            self.reader_thread.start()
            
            self.connection_changed.emit(True)
            self.status_label.setText(f"{self.ICON_CONNECTED} Connected to {self.port} @ {baud} baud")
            
        except serial.SerialException as e:
            self.output_text.append(f"Error opening serial port: {str(e)}")
            self.status_label.setText(f"{self.ICON_DISCONNECTED} Error: {str(e)[:50]}")
            self.connection_changed.emit(False)
        except Exception as e:
            self.output_text.append(f"Unexpected error: {str(e)}")
            self.status_label.setText(f"{self.ICON_DISCONNECTED} Error connecting")
            self.connection_changed.emit(False)
    
    def _read_serial_data(self):
        """Read serial data in background thread."""
        while self.running and self.serial_conn and self.serial_conn.is_open:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    try:
                        text = data.decode('utf-8', errors='replace')
                        self.data_received.emit(text)
                    except:
                        pass
                else:
                    time.sleep(0.01)
            except (serial.SerialException, OSError) as e:
                self.data_received.emit(f"\n[Connection lost: {str(e)}]\n")
                self.connection_changed.emit(False)
                break
            except Exception as e:
                time.sleep(0.1)
    
    def _append_output(self, text: str):
        """Append text to output area (thread-safe)."""
        self.output_text.insertPlainText(text)
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _update_status(self, connected: bool):
        """Update status label (thread-safe)."""
        if connected:
            self.status_label.setText(f"{self.ICON_CONNECTED} Connected to {self.port} @ {self.baud_selector.currentText()} baud")
        else:
            self.status_label.setText(f"{self.ICON_DISCONNECTED} Disconnected from {self.port}")
    
    def send_data(self):
        """Send data to serial port."""
        if not self.serial_conn or not self.serial_conn.is_open:
            QMessageBox.warning(self, "Error", "Serial monitor is not connected!")
            return
        
        data = self.send_input.text()
        if not data:
            return
        
        try:
            # Adicionar line ending
            ending = self.line_ending.currentText()
            if ending == "Newline (\\n)":
                data += '\n'
            elif ending == "Carriage Return (\\r)":
                data += '\r'
            elif ending == "Both (\\r\\n)":
                data += '\r\n'
            
            # Enviar dados
            self.serial_conn.write(data.encode('utf-8'))
            self.serial_conn.flush()
            
            # Mostrar no output
            self.output_text.insertPlainText(f"\n{self.ICON_SEND} Sent: {data}")
            self.send_input.clear()
            
        except serial.SerialTimeoutException:
            QMessageBox.warning(self, "Error", "Timeout sending data!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error sending data: {str(e)}")
    
    def change_baud_rate(self, new_baud: str):
        """Change the baud rate and reconnect."""
        if self.serial_conn and self.serial_conn.is_open:
            self.output_text.append(f"\n[Changing baud rate to {new_baud}...]\n")
            self.stop_monitor()
            time.sleep(0.5)
            self.start_monitor()
    
    def toggle_pause(self, paused: bool):
        """Toggle pause/resume of monitor output."""
        self.paused = paused
        if paused:
            self.pause_btn.setText(f"{self.ICON_PLAY} Resume")
        else:
            self.pause_btn.setText(f"{self.ICON_PAUSE} Pause")
    
    def stop_monitor(self):
        """Stop the serial monitor."""
        self.running = False
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2)
        
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except:
                pass
    
    def closeEvent(self, event):
        """Clean up resources on close."""
        self.stop_monitor()
        event.accept()