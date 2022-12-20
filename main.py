import sys

import PyQt6
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QIcon, QColor, QPainter
from PyQt6.QtWidgets import QWidget, QLabel, QStyle, QApplication, QPushButton, QMainWindow, QVBoxLayout


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        initial_name = QLabel(self)
        initial_name.setText('Cipher: encrypted note')
        initial_name.setStyleSheet('color: #ebebeb; background: transparent; size: 25')
        initial_name.setFont(font)
        self.w_max = 35

        self.button_close = QPushButton(self)
        self.button_close.setIcon(QIcon('assets/window_header/button_close.png'))
        self.button_close.setMinimumWidth(self.w_max)
        self.button_close.clicked.connect(lambda: self.close())

        self.button_collapse = QPushButton(self)
        self.button_collapse.setIcon(QIcon('assets/window_header/button_collapse.png'))
        self.button_collapse.setMinimumWidth(self.w_max)
        self.button_collapse.clicked.connect(lambda: self.showMinimized())

        self.button_full_screen = QPushButton(self)
        self.button_full_screen.setIcon(QIcon('assets/window_header/button_full_screen.png'))
        self.button_full_screen.setMinimumWidth(self.w_max)
        self.button_full_screen.clicked.connect(lambda: self.full_screen())
        self.full_window = False

        # self.button_close.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirClosedIcon))
        self.init_ui()

    def mousePressEvent(self, event):
        s = str(event.pos())
        if event.button() == Qt.MouseButton.LeftButton and int(s[s.index(', ') + 1:s.index(')')]) < 20:
            self._move()
            if event.type() == QEvent.Type.MouseButtonDblClick:
                self.full_screen()
            return super().mousePressEvent(event)

    def _move(self):
        window = self.window().windowHandle()
        window.startSystemMove()

    def click_browse(self):  # Обработка нажатия на кнопку 'browse'
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        # self.edt1.setText(str(folder_path).replace('/', "\\"))

    def full_screen(self):
        if not self.full_window:
            self.full_window = True
            self.showFullScreen()
        else:
            self.full_window = False
            self.showNormal()
        self.repaint_buttons()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()

    def drawRectangles(self, qp):
        col = QColor(24, 25, 28)
        qp.setPen(col)
        qp.setBrush(QColor(24, 25, 28))
        qp.drawRect(0, 0, self.width(), self.button_close.height() - 2)

    def repaint_buttons(self):
        self.button_close.move(self.width() - self.w_max, 0)
        self.button_full_screen.move(self.width() - self.w_max * 2, 0)
        self.button_collapse.move(self.width() - self.w_max * 3, 0)

    def init_ui(self):
        self.setGeometry(100, 100, 1200, 800)  # Размеры окна
        self.setWindowTitle('Cipher: encrypted note')
        self.setStyleSheet('background-color: #292828')
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.repaint_buttons()
        self.button_close.setStyleSheet('background: transparent; ')
        self.button_collapse.setStyleSheet('background: transparent;')
        self.button_full_screen.setStyleSheet('background: transparent;')
        self.button_close.setStyleSheet("QPushButton::hover{background-color : red;}")
        self.button_full_screen.setStyleSheet("QPushButton::hover{background-color : #858585;}")
        self.button_collapse.setStyleSheet("QPushButton::hover{background-color : #858585;}")
        # self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        # self.setWindowIcon(QIcon('pynote.png'))


app = QApplication(sys.argv)
font = QtGui.QFont()
font.setFamily('Calibri')
font.setPointSize(30)


def main():
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
