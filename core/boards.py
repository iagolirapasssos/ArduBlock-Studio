"""Board database definitions for ArduBlock Studio."""

BOARDS_DATABASE = [
    # ── UNO Family ──
    {"name": "Arduino UNO R3",              "fqbn": "arduino:avr:uno",                         "family": "UNO"},
    {"name": "Arduino UNO R4 Minima",       "fqbn": "arduino:renesas_uno:unor4minima",          "family": "UNO"},
    {"name": "Arduino UNO R4 WiFi",         "fqbn": "arduino:renesas_uno:unor4wifi",            "family": "UNO"},
    {"name": "Arduino UNO WiFi Rev2",       "fqbn": "arduino:megaavr:uno2018",                  "family": "UNO"},
    {"name": "Arduino UNO Mini LE",         "fqbn": "arduino:avr:uno",                         "family": "UNO"},
    # ── UNO Q Series ──
    {"name": "Arduino UNO Q (2GB)",         "fqbn": "arduino:renesas_uno:unor4wifi",            "family": "UNO Q"},
    {"name": "Arduino UNO Q (4GB)",         "fqbn": "arduino:renesas_uno:unor4wifi",            "family": "UNO Q"},
    # ── Nano Family ──
    {"name": "Arduino Nano",                "fqbn": "arduino:avr:nano",                        "family": "Nano"},
    {"name": "Arduino Nano (old bootloader)", "fqbn": "arduino:avr:nano:cpu=atmega328old",      "family": "Nano"},
    {"name": "Arduino Nano Every",          "fqbn": "arduino:megaavr:nona4809",                 "family": "Nano"},
    {"name": "Arduino Nano 33 BLE",         "fqbn": "arduino:mbed_nano:nano33ble",              "family": "Nano"},
    {"name": "Arduino Nano 33 BLE Sense",   "fqbn": "arduino:mbed_nano:nano33ble",              "family": "Nano"},
    {"name": "Arduino Nano 33 BLE Sense Rev2","fqbn":"arduino:mbed_nano:nano33blesense",        "family": "Nano"},
    {"name": "Arduino Nano 33 IoT",         "fqbn": "arduino:samd:nano_33_iot",                 "family": "Nano"},
    {"name": "Arduino Nano RP2040 Connect", "fqbn": "arduino:mbed_nano:nanorp2040connect",      "family": "Nano"},
    {"name": "Arduino Nano ESP32",          "fqbn": "arduino:esp32:nano_nora",                  "family": "Nano"},
    {"name": "Arduino Nano R4",             "fqbn": "arduino:renesas_uno:unor4minima",          "family": "Nano"},
    # ── Mega Family ──
    {"name": "Arduino Mega 2560",           "fqbn": "arduino:avr:mega",                        "family": "Mega"},
    {"name": "Arduino Mega 2560 Rev3",      "fqbn": "arduino:avr:mega",                        "family": "Mega"},
    {"name": "Arduino Mega ADK",            "fqbn": "arduino:avr:megaadk",                     "family": "Mega"},
    # ── Classic Family ──
    {"name": "Arduino Leonardo",            "fqbn": "arduino:avr:leonardo",                    "family": "Classic"},
    {"name": "Arduino Micro",               "fqbn": "arduino:avr:micro",                       "family": "Classic"},
    {"name": "Arduino Zero",                "fqbn": "arduino:samd:arduino_zero_native",         "family": "Classic"},
    {"name": "Arduino Due",                 "fqbn": "arduino:sam:arduino_due_x_dbg",            "family": "Classic"},
    {"name": "Arduino Pro Mini 5V/16MHz",   "fqbn": "arduino:avr:pro:cpu=16MHzatmega328",       "family": "Classic"},
    {"name": "Arduino Pro Mini 3.3V/8MHz",  "fqbn": "arduino:avr:pro:cpu=8MHzatmega328",        "family": "Classic"},
    {"name": "Arduino Lilypad USB",         "fqbn": "arduino:avr:LilyPadUSB",                  "family": "Classic"},
    # ── MKR Family ──
    {"name": "Arduino MKR Zero",            "fqbn": "arduino:samd:mkrzero",                    "family": "MKR"},
    {"name": "Arduino MKR WiFi 1010",       "fqbn": "arduino:samd:mkrwifi1010",                 "family": "MKR"},
    {"name": "Arduino MKR FOX 1200",        "fqbn": "arduino:samd:mkrfox1200",                  "family": "MKR"},
    {"name": "Arduino MKR WAN 1300",        "fqbn": "arduino:samd:mkrwan1300",                  "family": "MKR"},
    {"name": "Arduino MKR WAN 1310",        "fqbn": "arduino:samd:mkrwan1310",                  "family": "MKR"},
    {"name": "Arduino MKR GSM 1400",        "fqbn": "arduino:samd:mkrgsm1400",                  "family": "MKR"},
    {"name": "Arduino MKR NB 1500",         "fqbn": "arduino:samd:mkrnb1500",                   "family": "MKR"},
    {"name": "Arduino MKR Vidor 4000",      "fqbn": "arduino:samd:mkrvidor4000",                "family": "MKR"},
    # ── Portenta Family ──
    {"name": "Arduino Portenta H7",         "fqbn": "arduino:mbed_portenta:envie_m7",           "family": "Portenta"},
    {"name": "Arduino Portenta H7 Lite",    "fqbn": "arduino:mbed_portenta:envie_m7",           "family": "Portenta"},
    {"name": "Arduino Portenta H7 Lite Connected","fqbn":"arduino:mbed_portenta:envie_m7",      "family": "Portenta"},
    {"name": "Arduino Portenta X8",         "fqbn": "arduino:mbed_portenta:portenta_x8",        "family": "Portenta"},
    {"name": "Arduino Portenta C33",        "fqbn": "arduino:renesas_portenta:portenta_c33",    "family": "Portenta"},
    # ── Nicla Family ──
    {"name": "Arduino Nicla Sense ME",      "fqbn": "arduino:mbed_nicla:nicla_sense",           "family": "Nicla"},
    {"name": "Arduino Nicla Vision",        "fqbn": "arduino:mbed_nicla:nicla_vision",          "family": "Nicla"},
    {"name": "Arduino Nicla Voice",         "fqbn": "arduino:mbed_nicla:nicla_voice",           "family": "Nicla"},
    {"name": "Arduino Nicla Positioning",   "fqbn": "arduino:mbed_nicla:nicla_positioning",     "family": "Nicla"},
    # ── GIGA Family ──
    {"name": "Arduino GIGA R1 WiFi",        "fqbn": "arduino:mbed_giga:giga",                  "family": "GIGA"},
    # ── IoT / New (2024-2025) ──
    {"name": "Arduino Stella",              "fqbn": "arduino:mbed_nano:nano33ble",              "family": "IoT"},
    {"name": "Arduino Nesso N1",            "fqbn": "arduino:esp32:nano_nora",                  "family": "IoT"},
    # ── ESP Compatibles ──
    {"name": "ESP32 Dev Module",            "fqbn": "esp32:esp32:esp32",                       "family": "ESP32"},
    {"name": "ESP32-S3 Dev Module",         "fqbn": "esp32:esp32:esp32s3",                     "family": "ESP32"},
    {"name": "ESP8266 NodeMCU 1.0",         "fqbn": "esp8266:esp8266:nodemcuv2",               "family": "ESP8266"},
    {"name": "ESP8266 Wemos D1 Mini",       "fqbn": "esp8266:esp8266:d1_mini",                 "family": "ESP8266"},
]

def get_boards_by_family() -> dict:
    """Group boards by family."""
    families = {}
    for board in BOARDS_DATABASE:
        family = board["family"]
        if family not in families:
            families[family] = []
        families[family].append(board)
    return families

def find_board_by_fqbn(fqbn: str) -> dict:
    """Find a board by its FQBN."""
    for board in BOARDS_DATABASE:
        if board["fqbn"] == fqbn:
            return board
    return None

def get_default_board() -> dict:
    """Get the default board (Arduino UNO R3)."""
    return BOARDS_DATABASE[0]