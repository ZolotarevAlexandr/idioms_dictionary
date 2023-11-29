# TODO: Change DB interaction from SQL to ORM model

from PyQt5.QtWidgets import QMainWindow, QApplication
from ui.interfaces import Ui_MainWindow
import sys
from app_pages import DictionaryWindow, TranslationWindow, TestWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dict_button.pressed.connect(self.open_dict_window)
        self.trans_button.pressed.connect(self.open_trans_window)
        self.test_button.pressed.connect(self.open_test_window)

    def open_dict_window(self):
        self.dict_window = DictionaryWindow()
        self.dict_window.show()

    def open_trans_window(self):
        self.trans_window = TranslationWindow()
        self.trans_window.show()

    def open_test_window(self):
        self.test_window = TestWindow()
        self.test_window.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
