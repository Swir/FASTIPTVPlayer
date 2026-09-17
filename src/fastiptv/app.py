from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from . import __version__
from .enhanced_ui import EnhancedFastIPTVWindow
from .settings import load_settings


def resource_path(relative: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / relative


def main() -> int:
    if "--version" in sys.argv:
        print(f"FastIPTV Player {__version__}")
        return 0

    smoke_gui = "--smoke-gui" in sys.argv
    app = QApplication(sys.argv)
    app.setApplicationName("FastIPTV Player")
    app.setOrganizationName("Swir")
    icon = resource_path("assets/fastiptv.svg")
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    window = EnhancedFastIPTVWindow(load_settings(), smoke_mode=smoke_gui)
    window.show()
    if smoke_gui:
        # Validate QApplication, the real QMainWindow, menus, settings and Qt
        # platform plugins without touching a playlist, EPG endpoint or VLC.
        QTimer.singleShot(350, app.quit)
    return app.exec()
