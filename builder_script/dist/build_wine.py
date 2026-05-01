import sys, os
os.environ["WINEDEBUG"] = "-all"
sys.path.insert(0, r"/home/iaiaia/Documentos/Programacao/Python/ArduBlocks/ardublock_studio_new")
import PyInstaller.__main__
PyInstaller.__main__.run([
    "--onefile", "--windowed", "--clean", "--noconfirm",
    "--log-level=WARN",
    "--name=ArduBlockStudio",
    "--distpath=" + r"Z:\home\iaiaia\Documentos\Programacao\Python\ArduBlocks\ardublock_studio_new\dist\windows",
    "--hidden-import=PyQt6",
    "--hidden-import=PyQt6.QtCore",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=PyQt6.QtWebEngineWidgets",
    "--hidden-import=PyQt6.QtWebChannel",
    "--hidden-import=serial",
    "--exclude-module=tkinter",
    "--exclude-module=unittest",
    r"Z:\home\iaiaia\Documentos\Programacao\Python\ArduBlocks\ardublock_studio_new\main.py"
])
