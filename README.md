# ArduBlock Studio

<div align="center">

![ArduBlock Studio](https://img.shields.io/badge/ArduBlock-Studio-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.1-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge)
![Arduino](https://img.shields.io/badge/Arduino-Compatible-00979D?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)

**Visual Arduino Programming IDE for Everyone**

*Program Arduino visually by dragging and connecting blocks - no coding experience required!*

</div>

---

## 📚 Table of Contents

### For Teachers & Students
- [What is ArduBlock Studio?](#-what-is-ardublock-studio)
- [Quick Start Guide](#-quick-start-guide)
- [Download & Install](#-download--install)
- [First Project: Blink an LED](#-first-project-blink-an-led)
- [Available Examples](#-available-examples)

### For Developers
- [Technical Architecture](#-technical-architecture)
- [Project Structure](#-project-structure)
- [Development Setup](#-development-setup)
- [Building from Source](#-building-from-source)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)

---

## 👩‍🏫 What is ArduBlock Studio?

ArduBlock Studio is a **visual programming environment** that makes Arduino accessible to everyone. Instead of writing code, you **drag and drop colorful blocks** that snap together like puzzle pieces. It's perfect for:

- 🏫 **Teachers** introducing programming concepts
- 🧒 **Students** learning electronics and coding
- 🎨 **Makers** prototyping ideas quickly
- 👨‍👩‍👧 **Parents** doing STEM activities with kids

<img width="1366" height="738" alt="image" src="https://github.com/user-attachments/assets/87bf7736-eddf-4d5a-ba14-1c420673a020" />

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Drag blocks from the toolbox  →  Snap them together    │
│                                                          │
│  ┌──────────────┐     ┌──────────┐    ┌──────────────┐  │
│  │ Arduino      │     │ Turn on  │    │  Wait        │  │
│  │ Program      │────▶│ LED 13   │───▶│  1000 ms     │  │
│  └──────────────┘     └──────────┘    └──────────────┘  │
│                                            │             │
│                          ┌──────────┐      ▼             │
│                          │  Wait    │◀─────┘             │
│                          │  1000 ms │                    │
│                          └──────────┘                    │
│                              │                           │
│                              ▼                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  void setup() {                                  │   │
│  │    pinMode(13, OUTPUT);                          │   │
│  │  }                                               │   │
│  │  void loop() {                                   │   │
│  │    digitalWrite(13, HIGH);                       │   │
│  │    delay(1000);                                  │   │
│  │    digitalWrite(13, LOW);                        │   │
│  │    delay(1000);                                  │   │
│  │  }                                               │   │
│  └──────────────────────────────────────────────────┘   │
│           ↑ Real Arduino code is generated!             │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Step 1: Download

Choose your operating system:

<div align="center">

| Platform | Download | Size |
|----------|----------|------|
| 🪟 **Windows** | [**Download .exe**](https://drive.google.com/file/d/13TyDdDoamGr9VS7XixWzDTaUy_sg-TuL/view?usp=sharing) | ~80 MB |
| 🐧 **Linux** | [**Download AppImage**](https://drive.google.com/file/d/1VVV0PxfxcXLka0JVL0TvuiHCqr6pfxfG/view?usp=sharing) | ~75 MB |

</div>

### Step 2: Install Arduino CLI

ArduBlock Studio requires **arduino-cli** to upload code to your board:

- **Windows**: Download from [arduino-cli releases](https://arduino.github.io/arduino-cli/latest/installation/)
- **Linux**: `sudo apt install arduino-cli` or `curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh`
- **macOS**: `brew install arduino-cli`

### Step 3: Connect Your Arduino

1. Plug your Arduino board into a USB port
2. Open ArduBlock Studio
3. Click the **Refresh** button (🔄) to detect your board
4. Select your board and port from the dropdowns

### Step 4: Start Creating!

- Choose an example from the **Examples bar** or start from scratch
- Drag blocks from the **left panel** to the workspace
- Click **Verify** (⚙️) to check your code
- Click **Upload** (📤) to send to your Arduino

---

## 💡 First Project: Blink an LED

Let's make the built-in LED on pin 13 blink!

### What You Need
- Arduino board (UNO, Nano, Mega, etc.)
- USB cable

### Instructions

1. **Open ArduBlock Studio**
2. **Click "Blink LED"** in the Examples bar at the top
3. You'll see these blocks appear:

```
┌─────────────────────┐
│  Arduino Program    │
│ ┌─────────────────┐ │
│ │ Setup            │ │
│ │ ┌─────────────┐  │ │
│ │ │ Pin 13 = OUT │  │ │
│ │ └─────────────┘  │ │
│ │                  │ │
│ │ Loop             │ │
│ │ ┌─────────────┐  │ │
│ │ │ LED 13 ON   │  │ │
│ │ └──────┬──────┘  │ │
│ │        ▼         │ │
│ │ ┌─────────────┐  │ │
│ │ │ Wait 1000ms │  │ │
│ │ └──────┬──────┘  │ │
│ │        ▼         │ │
│ │ ┌─────────────┐  │ │
│ │ │ LED 13 OFF  │  │ │
│ │ └──────┬──────┘  │ │
│ │        ▼         │ │
│ │ ┌─────────────┐  │ │
│ │ │ Wait 1000ms │  │ │
│ │ └─────────────┘  │ │
│ └─────────────────┘ │
└─────────────────────┘
```

4. **Select your board** (Arduino UNO) and **port** (COM3 or /dev/ttyACM0)
5. Click **Upload** (📤)
6. **Watch the LED blink!** The small LED next to pin 13 will flash on and off every second.

### What's Happening?

The blocks generate this Arduino code:
```cpp
void setup() {
  pinMode(13, OUTPUT);     // Set pin 13 as output
}

void loop() {
  digitalWrite(13, HIGH);  // Turn LED on
  delay(1000);             // Wait 1 second
  digitalWrite(13, LOW);   // Turn LED off
  delay(1000);             // Wait 1 second
}
```

---

## 📚 Available Examples

ArduBlock Studio comes with **8 built-in examples** to help you learn:

<div align="center">

| Example | Icon | What You'll Learn |
|---------|------|-------------------|
| **Blink LED** | 💡 | Digital output, delays |
| **Traffic Light** | 🚦 | Multiple outputs, timing |
| **Serial Hello** | 📡 | Serial communication |
| **Servo Motor** | ⚙️ | Servo control, angles |
| **Ultrasonic** | 📏 | Sensor reading, distance |
| **Analog Sensor** | 📊 | Analog input |
| **LED PWM** | ✨ | PWM, brightness control |
| **Buzzer** | 🎵 | Tone generation, frequencies |

</div>

---

## 🖥️ Block Categories

| Category | Color | Description |
|----------|-------|-------------|
| **Structure** | 🟠 Orange | Program setup/loop, comments |
| **Functions** | 🟣 Purple | Create and call custom functions |
| **Digital Pins** | 🔵 Blue | pinMode, digitalWrite, digitalRead |
| **Analog Pins** | 🟢 Teal | analogWrite (PWM), analogRead |
| **Time** | 🟢 Green | delay, millis, micros |
| **Serial Monitor** | 🟣 Violet | Serial communication |
| **Control Flow** | 🔴 Red | if/else, while, for loops |
| **Math** | 🟢 Green | Arithmetic, map, constrain |
| **Logic** | 🟠 Orange | Comparisons, AND, OR, NOT |
| **Variables** | 🟠 Orange | Create and use variables |
| **LEDs & Outputs** | 🟡 Yellow | LED control, PWM, tone |
| **Servo Motor** | 🔴 Dark Red | Servo attach, write, read |
| **Sensors** | 🔵 Navy | Ultrasonic, DHT, LDR, Button |

---

## 🛠️ Technical Architecture *(For Developers)*

ArduBlock Studio is built on a **client-server architecture** where Python (PyQt6) serves as the backend and a WebView renders the Blockly interface.

### Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    ArduBlock Studio                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Frontend (JavaScript)                 │   │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────┐  │   │
│  │  │  Blockly   │  │  Theme   │  │    Bridge    │  │   │
│  │  │  v11.2     │  │  Custom  │  │  QWebChannel │  │   │
│  │  └────────────┘  └──────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                         ↕                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Backend (Python)                      │   │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────┐  │   │
│  │  │   PyQt6    │  │ Arduino  │  │  Permission  │  │   │
│  │  │  WebView   │  │   CLI    │  │   Manager    │  │   │
│  │  └────────────┘  └──────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Interaction
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Blockly    │────▶│    Bridge    │────▶│   Arduino    │
│   Workspace  │     │  (Signals)   │     │     CLI      │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Generated   │     │   Compile/   │     │   Hardware   │
│  C++ Code    │     │   Upload     │     │   (Arduino)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 📁 Project Structure

```
ardublock_studio/
├── main.py                        # Application entry point
├── build.py                       # Cross-platform build script
├── README.md                      # This file
│
├── config/                        # Configuration & permissions
│   ├── __init__.py
│   ├── permissions.py             # OS-specific permission setup
│   └── environment.py             # Dependency checking
│
├── core/                          # Core business logic
│   ├── __init__.py
│   ├── arduino_cli.py            # Arduino CLI wrapper
│   ├── boards.py                 # Board database (50+ boards)
│   └── library_manager.py        # Arduino library management
│
├── ui/                            # User interface components
│   ├── __init__.py
│   ├── main_window.py            # Main IDE window
│   ├── bridge.py                 # Python ↔ JavaScript bridge
│   ├── serial_monitor.py         # Serial monitor dialog
│   └── library_dialog.py         # Library manager dialog
│
├── resources/                     # Static resources
│   ├── __init__.py
│   └── blockly_html.py           # Complete Blockly HTML template
│
└── i18n/                          # Internationalization
    ├── __init__.py
    ├── translations.py           # Translation data class
    ├── en.py                     # English translations
    └── pt.py                     # Portuguese translations
```

---

## 💻 Development Setup

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **arduino-cli** (for compile/upload functionality)
- **Git** (for version control)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ardublock-studio.git
cd ardublock-studio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install PyQt6 PyQt6-WebEngine pyserial

# Run the application
python3 main.py
```

### IDE Setup (VS Code)

Recommended extensions:
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Black Formatter** (ms-python.black-formatter)

### Environment Variables

```bash
# Optional: Set custom arduino-cli path
export ARDUINO_CLI_PATH=/path/to/arduino-cli

# Optional: Set Wine prefix for Windows builds
export WINEPREFIX=~/.wine
```

---

## 🔨 Building from Source

### Using the Build Script

```bash
# Build for current OS only
python3 build.py

# Build all platforms
python3 build.py --all

# Force rebuild (ignore cache)
python3 build.py --linux --force

# Clean build cache
python3 build.py --clean --all

# Specify Wine Python path for cross-compilation
python3 build.py --windows --wine-python "/path/to/python.exe"
```

### Manual Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed \
  --name ArduBlockStudio \
  --hidden-import=PyQt6.QtWebEngineWidgets \
  --hidden-import=PyQt6.QtWebChannel \
  --hidden-import=serial \
  --hidden-import=config \
  --hidden-import=core \
  --hidden-import=ui \
  --hidden-import=resources \
  --hidden-import=i18n \
  --add-data "i18n:i18n" \
  --add-data "resources:resources" \
  main.py
```

### Platform-Specific Builds

#### Linux
```bash
python3 build.py --linux
# Output: dist/ardublock-studio-1.1-linux-x64.tar.gz
```

#### Windows (from Linux with Wine)
```bash
python3 build.py --windows
# Output: dist/ArduBlockStudio-1.1-windows-x64.zip
```

#### macOS
```bash
python3 build.py --mac
# Output: dist/ArduBlockStudio-1.1-macos-x64.zip
```

---

## 🔌 API Reference

### Bridge Interface

The `Bridge` class provides the communication layer between Python and JavaScript:

```python
class Bridge(QObject):
    # Signals (Python → JavaScript)
    boardsDetected = pyqtSignal(str)    # Connected boards JSON
    compileResult = pyqtSignal(str)     # Compilation result JSON
    uploadResult = pyqtSignal(str)      # Upload result JSON
    logMsg = pyqtSignal(str)            # Log messages
    
    # Slots (JavaScript → Python)
    @pyqtSlot()
    def detectBoards(self): ...
    
    @pyqtSlot(str, str)
    def compile(self, code: str, fqbn: str): ...
    
    @pyqtSlot(str, str, str)
    def upload(self, code: str, fqbn: str, port: str): ...
    
    @pyqtSlot(str)
    def setLanguage(self, lang: str): ...
```

### Arduino CLI Wrapper

```python
class ArduinoCLI:
    def is_available(self) -> bool: ...
    def detect_boards(self) -> List[Dict]: ...
    def compile(self, code: str, fqbn: str) -> Tuple[bool, str]: ...
    def upload(self, code: str, fqbn: str, port: str) -> Tuple[bool, str]: ...
    def get_version(self) -> str: ...
```

### Library Manager

```python
class LibraryManager:
    def search_libraries(self, query: str = "") -> List[Dict]: ...
    def get_popular_libraries(self) -> List[Dict]: ...
    def install_library(self, name: str) -> Tuple[bool, str]: ...
    def uninstall_library(self, name: str) -> Tuple[bool, str]: ...
    def install_from_zip(self, zip_path: str) -> Tuple[bool, str]: ...
```

---

## 🌐 Internationalization (i18n)

ArduBlock Studio supports multiple languages through a centralized translation system:

```python
from i18n.translations import Translations

# Create translations for a language
tr = Translations(language="pt")  # Portuguese

# Get translated text
title = tr.get("app_title")  # "ArduBlock Studio"
```

### Adding a New Language

1. Create `i18n/fr.py` (for French):
```python
FR_TRANSLATIONS = {
    "app_title": "ArduBlock Studio",
    "menu_new": "Nouveau",
    "menu_save": "Sauvegarder",
    # ... add all translations
}
```

2. Update `i18n/translations.py`:
```python
@dataclass
class Translations:
    language: str = "en"
    
    app_title: Dict[str, str] = field(default_factory=lambda: {
        "en": "ArduBlock Studio",
        "pt": "ArduBlock Studio",
        "fr": "ArduBlock Studio",  # Add French
    })
```

---

## 🧩 Custom Block Development

### Creating a New Block

1. **Define the block** in `blockly_html.py`:

```javascript
Blockly.Blocks['my_custom_block'] = {{
  init: function() {{
    this.setColour('#9966ff');
    this.appendDummyInput()
        .appendField("My Custom Block");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};
```

2. **Add code generator**:

```javascript
gen('my_custom_block', (b, g) => {{
  return '// Custom code here\\n';
}});
```

3. **Add to toolbox** (in the XML section):

```xml
<category name="Custom" colour="#9966ff">
  <block type="my_custom_block"></block>
</category>
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Contribution Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Code Style

- Follow **PEP 8** for Python code
- Use **meaningful variable names** (English)
- Add **docstrings** to all functions and classes
- Keep functions **small and focused** (< 50 lines)
- Write **descriptive commit messages**

### Testing

```bash
# Run the application in test mode
python3 main.py --test

# Test Arduino CLI communication
python3 -c "from core.arduino_cli import ArduinoCLI; cli = ArduinoCLI(); print(cli.get_version())"
```

### Bug Reports

When reporting bugs, please include:
- **Operating System** and version
- **Python version** (`python3 --version`)
- **arduino-cli version** (`arduino-cli version`)
- **Steps to reproduce** the issue
- **Error messages** from the console

---

## 📊 Supported Boards (50+)

<details>
<summary>Click to expand full list</summary>

| Family | Boards |
|--------|--------|
| **UNO** | UNO R3, UNO R4 Minima, UNO R4 WiFi, UNO WiFi Rev2, UNO Mini LE |
| **UNO Q** | UNO Q (2GB), UNO Q (4GB) |
| **Nano** | Nano, Nano Every, Nano 33 BLE, Nano 33 BLE Sense, Nano 33 IoT, Nano RP2040, Nano ESP32 |
| **Mega** | Mega 2560, Mega 2560 Rev3, Mega ADK |
| **Classic** | Leonardo, Micro, Zero, Due, Pro Mini, Lilypad |
| **MKR** | MKR Zero, MKR WiFi 1010, MKR FOX 1200, MKR WAN, MKR GSM 1400, MKR NB 1500, MKR Vidor 4000 |
| **Portenta** | Portenta H7, Portenta H7 Lite, Portenta X8, Portenta C33 |
| **Nicla** | Nicla Sense ME, Nicla Vision, Nicla Voice, Nicla Positioning |
| **GIGA** | GIGA R1 WiFi |
| **IoT** | Arduino Stella, Arduino Nesso N1 |
| **ESP** | ESP32 Dev Module, ESP32-S3, ESP8266 NodeMCU, Wemos D1 Mini |

</details>

---

## 🔧 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **"arduino-cli not found"** | Install from [arduino-cli releases](https://arduino.github.io/arduino-cli/latest/installation/) |
| **"Permission denied" on Linux** | Run: `sudo usermod -aG dialout $USER` and reboot |
| **Board not detected** | Check USB cable, try different port, press Reset button |
| **Upload fails (stk500 error)** | Select correct board type, press Reset before upload |
| **Serial Monitor not working** | Close other programs using the port (IDE, monitor) |
| **Blocks not generating code** | Make sure blocks are inside "Arduino Program" block |

### Getting Help

- 📖 Check the [Wiki](https://github.com/yourusername/ardublock-studio/wiki)
- 🐛 Report bugs on [Issues](https://github.com/yourusername/ardublock-studio/issues)
- 💬 Join the [Discussions](https://github.com/yourusername/ardublock-studio/discussions)

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 ArduBlock Studio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 🙏 Acknowledgments

- **[Blockly](https://developers.google.com/blockly)** - Visual programming library by Google
- **[Arduino CLI](https://arduino.github.io/arduino-cli/)** - Official Arduino command line tools
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** - Python bindings for Qt
- **[Material Icons](https://fonts.google.com/icons)** - Icon set by Google
- **[Arduino](https://www.arduino.cc/)** - Open-source electronics platform

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ for the Arduino community**

[Download Linux](https://drive.google.com/file/d/1VVV0PxfxcXLka0JVL0TvuiHCqr6pfxfG/view?usp=sharing) · [Download Windows](https://drive.google.com/file/d/13TyDdDoamGr9VS7XixWzDTaUy_sg-TuL/view?usp=sharing) · [Report Bug](https://github.com/yourusername/ardublock-studio/issues) · [Request Feature](https://github.com/yourusername/ardublock-studio/issues)

</div>
