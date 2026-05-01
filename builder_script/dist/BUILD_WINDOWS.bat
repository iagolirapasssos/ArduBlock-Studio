@echo off
chcp 65001 >nul
echo ========================================
echo   ArduBlock Studio - Build Windows
echo ========================================
echo.
pip install pyinstaller PyQt6 PyQt6-WebEngine pyserial --quiet
echo.
pyinstaller --onefile --windowed --name ArduBlockStudio --clean --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebChannel --hidden-import=serial --exclude-module=tkinter --exclude-module=unittest main.py
echo.
if exist "dist\ArduBlockStudio.exe" (echo ✅ SUCESSO! dist\ArduBlockStudio.exe) else (echo ❌ FALHA)
pause
