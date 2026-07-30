import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QProxyStyle
from PyQt5.QtGui import QPalette, QColor

from . import window, constants


# M3 Fusion proxy style — enhances Fusion with M3 shape awareness
class M3ProxyStyle(QProxyStyle):
    """A thin proxy over Fusion style to apply M3 shape tokens."""
    pass


# Main window class
#   Handles variables related to the main window.
#   Any actual program functionality or additional dialogs are
#   handled using different classes
class MainWindow:
    def __init__(self, qt_args):
        # Apply dark mode on Windows systems
        if constants.PLATFORM == constants.PlatformCode.WINDOWS:
            os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=1"

        # Make main objects
        self.app = QApplication(qt_args)
        self.window = window.MyQMainWindow()

        # Setup M3 base style: Fusion provides the best cross-platform base
        self.app.setStyle("fusion")

    def run(self):
        self.window.show()
        self.app.exec()


def main(args):
    if constants.HAS_SPLASH:
        import pyi_splash
        pyi_splash.close()

    main_window = MainWindow(args)
    main_window.run()


def run():
    main(sys.argv)
