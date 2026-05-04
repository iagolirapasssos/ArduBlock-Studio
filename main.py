#!/usr/bin/env python3
"""ArduBlock Studio - Visual Arduino Programming IDE."""
import sys
import platform
import importlib
import argparse  # Adicionar


def check_dependencies() -> bool:
    """Verify and install required dependencies."""
    dependencies = {
        "PyQt6": {"pip": "PyQt6", "imports": ["PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui"]},
        "PyQt6-WebEngine": {"pip": "PyQt6-WebEngine", "imports": ["PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore", "PyQt6.QtWebChannel"]},
        "pyserial": {"pip": "pyserial", "imports": ["serial"]}
    }
    
    missing = []
    for name, info in dependencies.items():
        found = False
        for module_path in info["imports"]:
            try:
                importlib.import_module(module_path)
                found = True
                break
            except ImportError:
                continue
        if not found:
            missing.append(info["pip"])
    
    if missing:
        print("=" * 60)
        print("DEPENDENCY CHECK FAILED")
        print(f"Missing: pip install {' '.join(missing)}")
        print("=" * 60)
        return False
    return True


def main():
    """Application entry point."""
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(description="ArduBlock Studio")
    parser.add_argument("--no-scan", action="store_true", 
                       help="Skip automatic board scanning on startup")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    args = parser.parse_args()
    
    print("=" * 60)
    print("ARDOBLOCK STUDIO - Starting...")
    if args.debug:
        print("DEBUG MODE ENABLED")
    print("=" * 60)
    
    if not check_dependencies():
        sys.exit(1)
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    
    from config.permissions import PermissionManager
    from ui.main_window import MainWindow
    from i18n.translations import Translations
    
    perm_manager = PermissionManager()
    perm_manager.setup()
    
    # INGLÊS COMO PADRÃO
    translations = Translations(language="en")
    
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass
    
    app = QApplication(sys.argv)
    app.setApplicationName("ArduBlock Studio")
    app.setApplicationVersion("1.1")
    app.setFont(QFont("Segoe UI", 10))
    
    print("Launching main window...")
    window = MainWindow(translations, no_scan=args.no_scan, debug=args.debug)
    window.show()
    print("Application running.")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()