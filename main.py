import string
import sys

import PyQt6
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint, QEvent, QRect, QPropertyAnimation, QTimer
from PyQt6.QtGui import QIcon, QColor, QPainter, QFontDatabase, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QStyle, QApplication, QPushButton, QMainWindow, QVBoxLayout, QFrame, \
    QHBoxLayout, QFormLayout, QGridLayout, QLineEdit
import random
import plyer
import sqlite3


def notify(text, title):  # Функция для уведомления пользователя, автоматически не скипается
    plyer.notification.notify(message=f'{text}', app_name='PyNote', app_icon=r'assets/pynote.ico',
                              title=title)

class Database:
    def __init__(self):
        pass


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initial_name = QLabel('Cipher: encrypted note', self)
        self.initial_name.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 60))
        self.initial_name.setStyleSheet(f'color: rgba(235, 235, 235, 1); background: transparent; size: 25;')
        self.initial_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.get_started = QLabel("Let's get started", self)
        self.get_started.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 30))
        self.get_started.setStyleSheet(f'color: #ebebeb; background: transparent; size: 25;')
        self.get_started.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input_path = QLineEdit(self)
        self.input_path.setPlaceholderText('Enter the path to the folder where the database will be stored ')
        self.input_path.setStyleSheet(f'color: #ebebeb; background: #18191c;')
        self.input_path.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 12))

        self.path_button = QPushButton(self)
        self.path_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirClosedIcon))
        self.path_button.setMinimumSize(self.input_path.height(), self.input_path.height())
        self.path_button.clicked.connect(lambda: self.click_browse())

        self.input_key = QLineEdit(self)
        self.input_key.setPlaceholderText('Think of a key that is 16 characters long')
        self.input_key.setStyleSheet(f'color: #ebebeb; background: #18191c;')
        self.input_key.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 12))
        self.input_key.setMinimumSize(self.input_path.width(), self.input_path.height())

        self.generate_button = QPushButton(self)
        self.generate_button.setIcon(QIcon('assets/interface/button_retry.png'))
        self.generate_button.setMinimumSize(self.input_path.height(), self.input_path.height())
        self.generate_button.clicked.connect(lambda: self.generate_key())
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

        self.timer = QTimer()
        self.alpha = 0.0
        self.timer.timeout.connect(lambda: self.animate_())
        self.timer.start(50)

        self.button_next = QPushButton('next', self)
        self.button_next.setStyleSheet(f'border-style: outset; border-radius: 6px;'
                                       f' color: rgba(235, 235, 235, 1); background: black; size: 25;')
        self.button_next.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 20))
        self.button_next.clicked.connect(lambda: self.next())

        self.init_ui()
        self.setFocus()

    def next(self):
        key = self.input_key.text()
        if len(self.input_key.text()) < 16:
            le = 16 - len(self.input_key.text())
            key = self.generate_key(le)
        elif len(self.input_key.text()) > 16:
            notify(self.input_key.text()[:16])
        notify(key, 'Remember your key!')

    def animate_(self):
        if self.alpha + 0.1 > 1.0:
            self.timer.disconnect()
        else:
            self.alpha += 0.1
            self.get_started.setStyleSheet(f'color: rgba(235, 235, 235, {self.alpha});'
                                           f' background: transparent; size: 25;')

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
        self.input_path.setText(str(folder_path).replace('/', "\\"))

    def generate_key(self, le=16):
        base = [i for i in string.ascii_lowercase + string.ascii_uppercase + string.digits
                + '/*-+@";:|=&?.,()<>!_']
        random.shuffle(base)
        key = str(''.join(base[:le]))
        self.input_key.setText(key)
        return key

    def full_screen(self):
        if not self.full_window:
            self.full_window = True
            self.showFullScreen()
        else:
            self.full_window = False
            self.showNormal()

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

    def init_ui(self):
        self.setGeometry(100, 100, 1200, 800)  # Размеры окна
        self.setWindowTitle('Cipher: encrypted note')
        self.setStyleSheet('background-color: #292828')
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.button_close.setStyleSheet('background: transparent; ')
        self.button_collapse.setStyleSheet('background: transparent;')
        self.button_full_screen.setStyleSheet('background: transparent;')
        self.button_close.setStyleSheet("QPushButton::hover{background-color : red;}")
        self.button_full_screen.setStyleSheet("QPushButton::hover{background-color : #858585;}")
        self.button_collapse.setStyleSheet("QPushButton::hover{background-color : #858585;}")

        main_layout = QFormLayout(self)
        main_layout.setSpacing(0)
        l_main = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        l2 = QGridLayout(self)
        l2.addWidget(self.button_collapse, 0, 0)
        l2.addWidget(self.button_full_screen, 0, 1)
        l2.addWidget(self.button_close, 0, 2)
        l2.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout(self)
        layout.addWidget(self.initial_name)
        layout.addWidget(self.get_started)

        layout_input_path = QHBoxLayout(self)
        layout_input_path.addWidget(self.input_path)
        layout_input_path.addWidget(self.path_button)
        layout_input_path.setSpacing(30)
        layout_input_path.setContentsMargins(300, 60, 300, 0)
        layout.addLayout(layout_input_path)

        layout_input_key = QHBoxLayout(self)
        layout_input_key.addWidget(self.input_key)
        layout_input_key.addWidget(self.generate_button)
        layout_input_key.setSpacing(30)
        layout_input_key.setContentsMargins(300, 60, 300, 0)
        layout.addLayout(layout_input_key)

        l3 = QVBoxLayout(self)
        l3.addWidget(self.button_next)
        self.button_next.setMinimumWidth(100)
        l3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l3.setContentsMargins(500, 60, 0, 0)
        layout.addLayout(l3)

        l_main.addLayout(l2)
        l_main.addLayout(layout)
        main_layout.addItem(l_main)
        # self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        # self.setWindowIcon(QIcon('pynote.png'))


app = QApplication(sys.argv)


def set_font(logo=False):
    if logo:
        id_font = QFontDatabase.addApplicationFont("assets/fonts/3270 Semi-Narrow 500.ttf")
    else:
        id_font = QFontDatabase.addApplicationFont("assets/fonts/GoogleSans-Bold.ttf")
    return id_font


def main():
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
