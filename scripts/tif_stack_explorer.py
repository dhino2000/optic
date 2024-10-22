import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from optic.apps.TIFStackExplorer.app import TIFStackExplorerGUI
from optic.gui.app_style import applyAppStyle

def main():
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    applyAppStyle(app)
    gui = TIFStackExplorerGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()