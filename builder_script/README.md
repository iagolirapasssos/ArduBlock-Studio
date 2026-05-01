# ArduBlock Studio Builder v3.6

Universal packaging tool for ArduBlock Studio that generates standalone executables for **Windows**, **Linux**, and **macOS** — no Python installation required for end users.

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [Platform-Specific Builds](#-platform-specific-builds)
- [Cross-Compilation](#-cross-compilation)
- [Command-Line Options](#-command-line-options)
- [Troubleshooting](#-troubleshooting)
- [Output Files](#-output-files)

---

## ✨ Features

- **Single-file executables** via PyInstaller
- **Cross-compilation** support (Linux → Windows via Wine, Windows → Linux via WSL)
- **Build caching** — skips already-built targets automatically
- **Force rebuild** option when source code changes
- **Distribution packages** — `.zip` for Windows, `.tar.gz` for Linux, `.app` for macOS
- **Scripts for manual builds** on systems without cross-compilation tools

---

## 📦 Requirements

### All Platforms
- **Python 3.8+** with `pip`
- **PyInstaller** (auto-installed if missing)
- **ArduBlock Studio source** (`ardublock_studio.py` in the same directory)

### Platform-Specific Dependencies

| Target Platform | Host Platform | Required Tools |
|----------------|---------------|----------------|
| **Linux** | Linux | None (native) |
| **Linux** | Windows | WSL (`wsl --install`) |
| **Linux** | macOS | Docker (`brew install docker`) |
| **Windows** | Windows | None (native) |
| **Windows** | Linux | Wine (`sudo apt install wine wine32`) |
| **Windows** | macOS | Wine (`brew install wine`) |
| **macOS** | macOS | None (native) |
| **macOS** | Linux/Windows | ❌ Requires macOS machine (or VM) |

---

## 🚀 Quick Start

```bash
# Clone or navigate to the project folder
cd ArduBlockStudio/

# Install Python dependencies (if not already done)
pip install pyinstaller PyQt6 PyQt6-WebEngine pyserial

# Build for your current platform
python3 build_all.py

# Output will be in the 'dist/' folder
```

### Build for a specific platform:

```bash
# Linux only
python3 build_all.py --linux

# Windows only
python3 build_all.py --windows

# macOS only (must be run on macOS)
python3 build_all.py --mac

# All platforms (if tools are available)
python3 build_all.py --all
```

---

## 🖥️ Platform-Specific Builds

### Linux (Native)

```bash
python3 build_all.py --linux
```

**Output:** `dist/ardublock-studio-3.6.0-linux-x64.tar.gz`

The Linux build works natively on any Linux distribution. No additional tools required.

**Installation on target machine:**
```bash
tar xzf ardublock-studio-3.6.0-linux-x64.tar.gz
cd ardublock-studio/
./ardublock-studio
```

---

### Windows (via Wine on Linux/macOS)

> **⚠️ Important:** Building for Windows on Linux/macOS requires Wine and a Windows version of Python installed inside Wine.

#### Step 1: Install Wine

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install wine wine32

# Fedora
sudo dnf install wine

# macOS
brew install wine
```

#### Step 2: Install Python inside Wine

Download Python 3.10 for Windows:
```bash
wget https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
```

Install silently:
```bash
wine python-3.10.11-amd64.exe /quiet InstallAllUsers=0 Include_test=0
```

#### Step 3: Find Python in Wine

Python may be installed in different locations depending on your system. Common paths include:

```
# Standard installation
~/.wine/drive_c/Python310/python.exe

# User-specific AppData (varies by username)
~/.wine/drive_c/users/<USERNAME>/Local Settings/Application Data/Programs/Python/Python310/python.exe

# Program Files
~/.wine/drive_c/Program Files/Python310/python.exe

# AppData Local
~/.wine/drive_c/users/<USERNAME>/AppData/Local/Programs/Python/Python310/python.exe
```

> **🔑 IMPORTANT:** The Python path inside Wine **varies from system to system** depending on:
> - Your Linux username
> - Wine version and configuration
> - Python installer options selected
> 
> **Example from the developer's machine:**
> ```
> /home/iaiaia/.wine/drive_c/users/iaiaia/Local Settings/Application Data/Programs/Python/Python310/python.exe
> ```
> 
> **Your path will likely be different.** Replace `iaiaia` with your actual username.

#### Step 4: Build

**Option A — Auto-detect (recommended):**
```bash
python3 build_all.py --windows
```

The script will automatically search for Python in common Wine locations.

**Option B — Specify path manually (more reliable):**
```bash
python3 build_all.py --windows --force \
  --wine-python "/home/YOUR_USERNAME/.wine/drive_c/users/YOUR_USERNAME/Local Settings/Application Data/Programs/Python/Python310/python.exe"
```

**Option C — Run on a real Windows machine:**
```bash
# Copy these files to Windows:
#   - ardublock_studio.py
#   - dist/BUILD_WINDOWS.bat

# Then run on Windows:
BUILD_WINDOWS.bat
```

**Output:** `dist/ArduBlockStudio-3.6.0-windows-x64.zip`

---

### macOS (Native only)

> **⚠️ macOS builds can only be created on macOS.** Cross-compilation from Linux/Windows is not supported.

```bash
python3 build_all.py --mac
```

Or copy the generated script to a Mac:
```bash
# On macOS:
./build_macos.sh
```

**Output:** `dist/ArduBlockStudio.app`

---

## 🔄 Cross-Compilation

### Linux → Windows (via Wine)

```bash
# 1. Install Wine
sudo apt install wine wine32

# 2. Kill any existing Wine processes
wineserver -k

# 3. Build
python3 build_all.py --windows --force

# Or with explicit Python path:
python3 build_all.py --windows --force \
  --wine-python "PATH_TO_PYTHON_IN_WINE"
```

### Windows → Linux (via WSL)

```cmd
:: 1. Install WSL (run in PowerShell as Admin)
wsl --install

:: 2. Build
python build_all.py --linux
```

### Docker (experimental)

```bash
# Linux build via Docker
python3 build_all.py --linux
# (uses Docker automatically if not on Linux)
```

---

## 📋 Command-Line Options

| Option | Description |
|--------|-------------|
| `--linux` | Build for Linux only |
| `--windows` | Build for Windows only |
| `--mac` | Build for macOS only |
| `--all` | Build for all platforms |
| `--force` | Force rebuild (ignore cache) |
| `--clean` | Clear build cache before starting |
| `--wine-python PATH` | Specify Python path in Wine manually |
| `--no-package` | Skip creating `.zip`/`.tar.gz` packages |

### Examples

```bash
# Force rebuild for Linux
python3 build_all.py --linux --force

# Clean cache and rebuild Windows
python3 build_all.py --windows --clean --force

# Windows with explicit Wine Python path
python3 build_all.py --windows \
  --wine-python "~/.wine/drive_c/Python310/python.exe" \
  --force

# Build Linux + Windows (skip macOS)
python3 build_all.py --linux --windows

# Build everything with force
python3 build_all.py --all --force
```

---

## ⚠️ Troubleshooting

### Wine Issues

**Problem:** Wine hangs or shows `fixme` warnings
```bash
# Kill all Wine processes
wineserver -k

# Retry with clean Wine state
python3 build_all.py --windows --force
```

**Problem:** Python not found in Wine
```bash
# Search for Python manually
find ~/.wine -name "python.exe" -type f 2>/dev/null

# Use the found path
python3 build_all.py --windows --wine-python "FOUND_PATH"
```

**Problem:** Wine Python can't install packages
```bash
# Try installing manually
wine "~/.wine/drive_c/.../python.exe" -m pip install pyinstaller PyQt6 PyQt6-WebEngine pyserial
```

**Problem:** `urlmon.dll` or other DLL errors
```bash
# Install missing Wine components
winetricks corefonts
winetricks vcrun2019
```

### Build Fails

**Problem:** Out of memory during build
```bash
# Close other applications
# Ensure at least 4GB RAM available
# Add swap if needed: sudo fallocate -l 4G /swapfile
```

**Problem:** Disk space
```bash
# Each build requires ~2GB temporary space
df -h
# Clean old builds
rm -rf dist/build dist/specs
```

### macOS Gatekeeper

If users get "unidentified developer" warning:
```bash
# On the target Mac:
xattr -cr /path/to/ArduBlockStudio.app
# Or: System Preferences → Security & Privacy → Open Anyway
```

---

## 📁 Output Files

After a successful build, the `dist/` folder contains:

```
dist/
├── linux/
│   └── ardublock-studio                    # Linux executable
├── windows/
│   └── ArduBlockStudio.exe                 # Windows executable
├── macos/
│   └── ArduBlockStudio.app                 # macOS application bundle
├── ArduBlockStudio-3.6.0-windows-x64.zip   # Windows distribution
├── ardublock-studio-3.6.0-linux-x64.tar.gz # Linux distribution
├── BUILD_WINDOWS.bat                       # Script for Windows build
├── build_macos.sh                          # Script for macOS build
├── VERSION.txt                             # Build information
└── .cache/                                 # Build cache (do not distribute)
```

### Distribution Checklist

- **Linux users:** Send `ardublock-studio-*.tar.gz` — extract and run
- **Windows users:** Send `ArduBlockStudio-*.zip` — extract and run `.exe`
- **macOS users:** Send the `.app` bundle — drag to Applications folder

---

## 🔧 Python Path in Wine Reference

The location of Python inside Wine depends on several factors. Here are all possible paths the builder searches:

```
1.  ~/.wine/drive_c/Python310/python.exe
2.  ~/.wine/drive_c/Python311/python.exe
3.  ~/.wine/drive_c/Program Files/Python310/python.exe
4.  ~/.wine/drive_c/Program Files (x86)/Python310/python.exe
5.  ~/.wine/drive_c/users/<USER>/Local Settings/Application Data/Programs/Python/Python310/python.exe
6.  ~/.wine/drive_c/users/<USER>/AppData/Local/Programs/Python/Python310/python.exe
7.  ~/.wine/drive_c/users/<USER>/AppData/Roaming/Python/Python310/python.exe
```

> **Note:** Replace `<USER>` with your Linux username. The builder automatically detects your username.

To find your exact path:
```bash
find ~/.wine -name "python.exe" -size +10k 2>/dev/null
```

---

## 📄 License

This project is distributed under the MIT License. See the ArduBlock Studio main repository for details.

---

## 🤝 Contributing

To add support for additional platforms or improve cross-compilation:

1. Fork the repository
2. Add your build method to `UniversalPackager`
3. Submit a pull request

---

**Built with ❤️ for the Arduino community**