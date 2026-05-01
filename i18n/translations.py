"""Translation manager for ArduBlock Studio."""
from dataclasses import dataclass, field
from typing import Dict
import json


@dataclass
class Translations:
    """Centralized translations for the application."""
    
    # Language code
    language: str = "en"
    
    # UI Translations
    app_title: Dict[str, str] = field(default_factory=lambda: {
        "en": "ArduBlock Studio",
        "pt": "ArduBlock Studio"
    })
    
    app_subtitle: Dict[str, str] = field(default_factory=lambda: {
        "en": "Visual Arduino Programming IDE for children and teenagers",
        "pt": "IDE visual de programação Arduino para crianças e adolescentes"
    })
    
    menu_new: Dict[str, str] = field(default_factory=lambda: {
        "en": "New",
        "pt": "Novo"
    })
    
    menu_save: Dict[str, str] = field(default_factory=lambda: {
        "en": "Save",
        "pt": "Salvar"
    })
    
    menu_open: Dict[str, str] = field(default_factory=lambda: {
        "en": "Open",
        "pt": "Abrir"
    })
    
    btn_verify: Dict[str, str] = field(default_factory=lambda: {
        "en": "Verify",
        "pt": "Verificar"
    })
    
    btn_upload: Dict[str, str] = field(default_factory=lambda: {
        "en": "Upload",
        "pt": "Enviar"
    })
    
    btn_serial: Dict[str, str] = field(default_factory=lambda: {
        "en": "Serial",
        "pt": "Serial"
    })
    
    board_label: Dict[str, str] = field(default_factory=lambda: {
        "en": "Board",
        "pt": "Placa"
    })
    
    port_label: Dict[str, str] = field(default_factory=lambda: {
        "en": "Port",
        "pt": "Porta"
    })
    
    status_ready: Dict[str, str] = field(default_factory=lambda: {
        "en": "Ready",
        "pt": "Pronto"
    })
    
    status_compile_success: Dict[str, str] = field(default_factory=lambda: {
        "en": "Compilation successful",
        "pt": "Compilação bem-sucedida"
    })
    
    status_upload_success: Dict[str, str] = field(default_factory=lambda: {
        "en": "Upload successful! Program sent to Arduino.",
        "pt": "Upload concluído! Programa enviado para o Arduino."
    })
    
    msg_no_board: Dict[str, str] = field(default_factory=lambda: {
        "en": "Select a board!",
        "pt": "Selecione uma placa!"
    })
    
    msg_no_port: Dict[str, str] = field(default_factory=lambda: {
        "en": "Select the board port!",
        "pt": "Selecione a porta da placa!"
    })
    
    msg_no_cli: Dict[str, str] = field(default_factory=lambda: {
        "en": "arduino-cli not found. Install from: https://arduino.github.io/arduino-cli",
        "pt": "arduino-cli não encontrado. Instale em: https://arduino.github.io/arduino-cli"
    })
    
    monitor_title: Dict[str, str] = field(default_factory=lambda: {
        "en": "Serial Monitor",
        "pt": "Monitor Serial"
    })
    
    monitor_baud_label: Dict[str, str] = field(default_factory=lambda: {
        "en": "Baud Rate:",
        "pt": "Baud Rate:"
    })
    
    monitor_clear: Dict[str, str] = field(default_factory=lambda: {
        "en": "Clear",
        "pt": "Limpar"
    })
    
    monitor_pause: Dict[str, str] = field(default_factory=lambda: {
        "en": "Pause",
        "pt": "Pausar"
    })
    
    monitor_resume: Dict[str, str] = field(default_factory=lambda: {
        "en": "Resume",
        "pt": "Retomar"
    })
    
    monitor_send: Dict[str, str] = field(default_factory=lambda: {
        "en": "Send",
        "pt": "Enviar"
    })
    
    monitor_close: Dict[str, str] = field(default_factory=lambda: {
        "en": "Close Monitor",
        "pt": "Fechar Monitor"
    })
    
    category_structure: Dict[str, str] = field(default_factory=lambda: {
        "en": "Structure",
        "pt": "Estrutura"
    })
    
    category_digital: Dict[str, str] = field(default_factory=lambda: {
        "en": "Digital Pins",
        "pt": "Pinos Digitais"
    })
    
    category_analog: Dict[str, str] = field(default_factory=lambda: {
        "en": "Analog Pins",
        "pt": "Pinos Analógicos"
    })
    
    category_time: Dict[str, str] = field(default_factory=lambda: {
        "en": "Time",
        "pt": "Tempo"
    })
    
    category_serial: Dict[str, str] = field(default_factory=lambda: {
        "en": "Serial Monitor",
        "pt": "Monitor Serial"
    })
    
    category_control: Dict[str, str] = field(default_factory=lambda: {
        "en": "Control Flow",
        "pt": "Controle de Fluxo"
    })
    
    category_math: Dict[str, str] = field(default_factory=lambda: {
        "en": "Mathematics",
        "pt": "Matemática"
    })
    
    category_logic: Dict[str, str] = field(default_factory=lambda: {
        "en": "Logic",
        "pt": "Lógica"
    })
    
    category_variables: Dict[str, str] = field(default_factory=lambda: {
        "en": "Variables",
        "pt": "Variáveis"
    })
    
    category_leds: Dict[str, str] = field(default_factory=lambda: {
        "en": "LEDs and Outputs",
        "pt": "LEDs e Saídas"
    })
    
    category_servo: Dict[str, str] = field(default_factory=lambda: {
        "en": "Servo Motor",
        "pt": "Servo Motor"
    })
    
    category_sensors: Dict[str, str] = field(default_factory=lambda: {
        "en": "Sensors",
        "pt": "Sensores"
    })
    
    category_functions: Dict[str, str] = field(default_factory=lambda: {
        "en": "Functions",
        "pt": "Funções"
    })
    
    code_panel_title: Dict[str, str] = field(default_factory=lambda: {
        "en": "GENERATED CODE",
        "pt": "CÓDIGO GERADO"
    })
    
    console_title: Dict[str, str] = field(default_factory=lambda: {
        "en": "CONSOLE",
        "pt": "CONSOLE"
    })
    
    examples_label: Dict[str, str] = field(default_factory=lambda: {
        "en": "Examples:",
        "pt": "Exemplos:"
    })
    
    ex_blink: Dict[str, str] = field(default_factory=lambda: {
        "en": "Blink LED",
        "pt": "Piscar LED"
    })
    
    ex_traffic: Dict[str, str] = field(default_factory=lambda: {
        "en": "Traffic Light",
        "pt": "Semáforo"
    })
    
    ex_serial_hello: Dict[str, str] = field(default_factory=lambda: {
        "en": "Serial Hello",
        "pt": "Serial Hello"
    })
    
    ex_servo: Dict[str, str] = field(default_factory=lambda: {
        "en": "Servo Motor",
        "pt": "Servo Motor"
    })
    
    ex_ultrasonic: Dict[str, str] = field(default_factory=lambda: {
        "en": "Ultrasonic",
        "pt": "Ultrassônico"
    })
    
    ex_analog: Dict[str, str] = field(default_factory=lambda: {
        "en": "Analog Sensor",
        "pt": "Sensor Analógico"
    })
    
    ex_pwm: Dict[str, str] = field(default_factory=lambda: {
        "en": "LED PWM",
        "pt": "LED PWM"
    })
    
    ex_tone: Dict[str, str] = field(default_factory=lambda: {
        "en": "Buzzer",
        "pt": "Buzzer"
    })

    # Variáveis
    var_global: Dict[str, str] = field(default_factory=lambda: {
        "en": "Global",
        "pt": "Global"
    })
    
    var_local: Dict[str, str] = field(default_factory=lambda: {
        "en": "Local",
        "pt": "Local"
    })

    def get(self, key: str, default: str = "") -> str:
        """Get translated string for current language."""
        if hasattr(self, key):
            translations_dict = getattr(self, key)
            if isinstance(translations_dict, dict):
                return translations_dict.get(self.language, default)
        return default
    
    def t(self, key: str, **kwargs) -> str:
        """Get translated string with formatting."""
        text = self.get(key, f"{{MISSING:{key}}}")
        return text.format(**kwargs) if kwargs else text

    def to_json(self) -> str:
        """Export all translations as JSON for JavaScript."""
        import json
        result = {}
        for key in dir(self):
            if not key.startswith('_') and key not in ('language', 'to_json', 'get_all', 'get', 't'):
                value = getattr(self, key)
                if isinstance(value, dict):
                    result[key] = value
        return json.dumps(result)
    
    def get_all(self) -> dict:
        """Get all translations for current language."""
        result = {}
        for key in dir(self):
            if not key.startswith('_') and key not in ('language', 'to_json', 'get_all', 'get', 't'):
                value = getattr(self, key)
                if isinstance(value, dict):
                    result[key] = value.get(self.language, key)
        return result