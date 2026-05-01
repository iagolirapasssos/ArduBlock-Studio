#!/bin/bash
pip3 install pyinstaller PyQt6 PyQt6-WebEngine pyserial --quiet
pyinstaller --onefile --windowed --name ArduBlockStudio --clean --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel --hidden-import=serial --exclude-module=tkinter --exclude-module=unittest --osx-bundle-identifier=com.ardublock.studio main.py
[ -d "dist/ArduBlockStudio.app" ] && echo "✅ SUCESSO!" || echo "❌ FALHA"
