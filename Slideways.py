import sys

from PyQt5.QtWidgets import QApplication

from GUI import Window, errorBox


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        ex = Window()
        sys.exit(app.exec_())
    except Exception as e:
        errorBox(e)
