import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog
from main_form import Ui_MainWindow
from data_change_form import Ui_Dialog


class ChangingForm(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.dead_tabl.setColumnCount(5)
        # self.dead_tabl.setRowCount(5)
        # self.dead_tabl.setItem(0, 0, QTableWidgetItem("123123"))
        # self.dead_tabl.resizeColumnsToContents()
        self.show_data()
        self.add_dead_btn.clicked.connect(self.change_data)
        self.add_ttab_btn.clicked.connect(self.change_data)
        self.chg_dead_btn.clicked.connect(self.change_data)
        self.chg_ttab_btn.clicked.connect(self.change_data)
        self.parents = [self.dead_btns, self.ttab_btns]
        self.tables = []
        self.parent_to_table = zip(self.parents, self.tables)
        self.changing_form = ChangingForm()

    def change_data(self):
        self.changing_form.show()
        self.parent_to_table[self.sender().parent()]

    def show_data(self):
        pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    c = Main()
    c.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
