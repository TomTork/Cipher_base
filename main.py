import hashlib
import os
import random
import sqlite3
import string
import sys
import firebase_admin
from PyQt6.uic.properties import QtGui
from firebase_admin import credentials
from firebase_admin import db
import plyer
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, QEvent, QTimer
from PyQt6.QtGui import QIcon, QColor, QPainter, QFontDatabase, QFont, QShortcut, QKeySequence, QStandardItemModel, \
    QStandardItem, QKeyEvent
from PyQt6.QtWidgets import QWidget, QLabel, QStyle, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, \
    QGridLayout, QLineEdit, QDialog, QDialogButtonBox, QMessageBox, QStackedLayout, QLayout, QGraphicsAnchorLayout, \
    QListWidget, QListView, QAbstractItemView


def notify(text, title):  # Функция для уведомления пользователя, автоматически не скипается
    plyer.notification.notify(message=f'{text}', app_name='PyNote', app_icon=r'assets/pynote.ico',
                              title=title)


def generate_hash(key):
    m = hashlib.sha256()
    m.update(bytes(key, 'utf-8'))
    return str(m.hexdigest())


class Database:
    def __init__(self, path=''):
        self.path_ = ''
        if not os.path.isfile(f'/path.txt'):
            conn = sqlite3.connect(f'{path}/database.db')
            c = conn.cursor()
            c.execute("""
                                create table if not exists main(
                                identity integer,
                                hash_key text,
                                resolution_main text,
                                resolution_note text,
                                firebase1 integer,
                                login1 text,
                                password1 text);       
                                            """)
            conn.commit()
            c.execute('''insert into main values(0, "empty", "1200x800", "1920x1080", 0, "", "")''')
            conn.commit()
        self.path_ = open('path.txt').readline()

    def get_login(self):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute('select login_ from main where identity=0')
        temp = c.fetchone()[0]
        conn.close()
        return temp

    def get_password(self):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute('select password1 from main where identity=0')
        temp = c.fetchone()[0]
        conn.close()
        return temp

    def set_password(self, value):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute(f'update main set password1="{value}" where identity=0')
        conn.commit()
        conn.close()

    def set_login(self, value):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute(f'update main set login1="{value}" where identity=0')
        conn.commit()
        conn.close()

    def get_firebase(self):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute('select firebase1 from main where identity=0')
        temp = int(c.fetchone()[0])
        conn.close()
        if temp == 1:
            return True
        return False

    def set_firebase(self, value: int):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        print('xxx', self.path_)
        c.execute(f'update main set firebase1={value} where identity=0')
        conn.commit()
        conn.close()

    def set_resolution_note(self, x, y):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute(f'update main set resolution_note="({x}x{y})" where identity=0')
        conn.commit()
        conn.close()

    def set_resolution_main(self, x, y):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute(f'update main set resolution_main="({x}x{y})" where identity=0')
        conn.commit()
        conn.close()

    def get_resolution_note(self):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute('select resolution_note from main where identity=0')
        temp = c.fetchone()[0]
        conn.close()
        return temp

    def get_resolution_main(self):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute('select resolution_main from main where identity=0')
        temp = c.fetchone()[0]
        conn.close()
        return temp

    def set_hash(self, key):
        value = generate_hash(key)
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute(f'update main set hash_key="{value}" where identity=0')
        conn.commit()
        conn.close()

    def get_hash(self):
        conn = sqlite3.connect(f'{self.path_}/database.db')
        c = conn.cursor()
        c.execute('select hash_key from main where identity=0')
        temp = c.fetchone()[0]
        conn.close()
        return temp


class BaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.w_max = 35
        self.g_list = []
        self.index_click = []

        self.current_w = 0
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

        shortcut_add = QShortcut(QKeySequence("ctrl+t"), self)
        shortcut_add.activated.connect(lambda: self.new_note())
        shortcut_close = QShortcut(QKeySequence('ctrl+w'), self)
        shortcut_close.activated.connect(lambda: self.close_note())
        shortcut_next = QShortcut(QKeySequence('ctrl+tab'), self)
        shortcut_next.activated.connect(lambda: self.next_note())

        # new_note_button = QPushButton(self)
        # new_note_button.setText('New note')
        # new_note_button.setStyleSheet(f'border-style: outset; border-radius: 6px;'
        #                               f' color: rgba(235, 235, 235, 1); background: black; size: 25;')
        # new_note_button.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 12))

        self.main_window = QPushButton(self)
        self.main_window.setText('Main menu')
        self.main_window.setIcon(QIcon('assets/interface/main_button.png'))
        self.main_window.setStyleSheet('QPushButton{color: white; max-width: 150;}'
                                       ' QPushButton::hover{background-color : #858585;};')
        self.main_window.setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 12))
        self.init_ui()

        self.list_tabs = []
        self.update_buttons()

        void = QLabel(self)
        self.add_items(self.list_tabs)
        self.add_item(void)
        self.setFocus()

    def add_button(self, text):
        self.list_tabs.append(QPushButton(self, text=text))
        if text not in self.g_list:
            self.g_list.append(text)
        self.update_buttons()

    def update_buttons(self):
        for i in range(len(self.list_tabs)):
            if i <= len(self.g_list):
                if self.list_tabs[i].text() not in self.g_list:
                    self.g_list.append(self.list_tabs[i].text())
            else:
                self.g_list[i] = self.list_tabs[i].text()
            if i not in self.index_click:
                self.list_tabs[i].clicked.connect(lambda: self.click_button_list())
                self.index_click.append(i)

    def click_button_list(self):
        rbt = self.sender()
        index = self.g_list.index(str(rbt.text()))
        print(index)

    def add_items(self, items, texts=None):
        for i in range(len(items)):
            try:
                items[i].setText(texts[i])
                self.g_list[i] = texts[i]
            except BaseException:
                pass
            items[i].setStyleSheet('QPushButton{color: white; max-width: 150;}'
                                   ' QPushButton::hover{background-color : #858585;};')
            items[i].setFont(QFont(QFontDatabase.applicationFontFamilies(set_font(False)), 10))
            self.h1.addWidget(items[i])

    def add_item(self, item, text=None):
        if text is not None:
            item.setText(text)
        self.h1.addWidget(item)

    def new_note(self):
        print('new note')

    def close_note(self):
        print('closed')

    def next_note(self):
        try:
            self.current_w += 1
        except BaseException:
            self.current_w = 0

    def current_window(self, number):
        try:
            self.current_w = number
        except BaseException:
            self.current_w = 0

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
        l_main = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        l2 = QGridLayout(self)
        l2.addWidget(self.button_collapse, 0, 0)
        l2.addWidget(self.button_full_screen, 0, 1)
        l2.addWidget(self.button_close, 0, 2)
        l2.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.h1 = QHBoxLayout(self)
        self.h1.setSpacing(2)
        self.h1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.h1.addWidget(self.main_window)

        self.vv = QVBoxLayout(self)

        l_main.addLayout(l2)
        l_main.addLayout(self.h1)
        main_layout.addItem(l_main)
        self.setLayout(main_layout)

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


class Firebase:
    def __init__(self):
        self.cred = credentials.Certificate('firebase.json')
        v = firebase_admin.initialize_app(self.cred, {
            'databaseURL': 'https://cipher-base-default-rtdb.firebaseio.com/'
        })

    def create_user(self, password):
        global database
        ref = db.reference('/')
        ref.set({
            f'{database.get_login()}': {
                'password': f'{password}',
                'note': ''
            }
        })


class RegistrationDialog(QDialog):
    def __init__(self, labels, parent=None, main_=None):
        super().__init__(parent)
        self.main_ = main_
        self.setWindowIcon(QIcon('assets/pynote.ico'))
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                      | QDialogButtonBox.StandardButton.Cancel, self)
        self.setWindowTitle('Registration')
        layout = QFormLayout(self)
        layout.addWidget(QLabel('Registration in firebase to synchronize / save notes'
                                '\nYou can skip this step', self))
        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])
        self.inputs[0].setPlaceholderText('Login')
        self.inputs[1].setPlaceholderText('Password')
        layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self.ok())
        button_box.rejected.connect(lambda: self.cancel())

    def get_inputs(self):
        return tuple(input.text() for input in self.inputs)

    def ok(self):  # Обработка нажатия на кнопку 'ок'
        global database, firebase
        firebase.create_user(generate_hash(self.get_inputs()[1]))
        try:
            database.set_firebase(1)
        except BaseException:
            database.set_firebase(0)

    def cancel(self):
        global database
        self.main_.close()
        self.close()
        base_window = BaseWindow()
        base_window.show()


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.w_max = 35
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
        global database
        key = self.input_key.text()
        if len(self.input_key.text()) < 16:
            le = 16 - len(self.input_key.text())
            key += self.generate_key(le)
            notify(key, 'Remember your key!')
            self.input_key.setText(key)
        elif len(self.input_key.text()) > 16:
            key = self.input_key.text()[:16]
            notify(key, 'Remember your key!')
            self.input_key.setText(key)
        else:
            notify(key, 'Remember your key!')
        try:
            f = open('path.txt', 'w')
            f.write(self.input_path.text())
            f.close()
            create_database(self.input_path.text())
            database.set_hash(key)
            registration_dialog = RegistrationDialog(labels=['Login', 'Password'], main_=self)
            registration_dialog.exec()
        except BaseException:
            notify('Error: check the input path or another problem', 'Error')

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

database = None
firebase = Firebase()


def create_database(path):
    global database
    database = Database(path)


def set_font(logo=False):
    if logo:
        id_font = QFontDatabase.addApplicationFont("assets/fonts/3270 Semi-Narrow 500.ttf")
    else:
        id_font = QFontDatabase.addApplicationFont("assets/fonts/GoogleSans-Bold.ttf")
    return id_font


def main():
    try:
        f = open('path.txt', 'r')
        create_database(f.readline())
        f.close()
        base_window = BaseWindow()
        base_window.show()
    except BaseException:
        start_window = StartWindow()
        start_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
