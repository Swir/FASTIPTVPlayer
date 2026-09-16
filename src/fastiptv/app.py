from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from . import __version__
from .settings import load_settings
from .ui import FastIPTVWindow


def resource_path(relative: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return root / relative


def main() -> int:
    if "--version" in sys.argv:
        print(f"FastIPTV Player {__version__}")
        return 0
    app = QApplication(sys.argv)
    app.setApplicationName("FastIPTV Player")
    app.setOrganizationName("Swir")
    icon = resource_path("assets/fastiptv.svg")
    if icon.exists():
        app.setWindowIcon(QIcon(str(icon)))
    window = FastIPTVWindow(load_settings())
    window.show()
    return app.exec()
