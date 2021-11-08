import sqlite3
import sys
from datetime import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog
from main_form import Ui_MainWindow
from data_change_form import Ui_Dialog


class TableElementTime:
    def __init__(self, *args):
        self.date_of_start = args[0]
        self.time_of_start = args[1]
        self.period = args[2]
        self.date_of_end = args[3]
        self.time_of_end = args[4]

    def make_add_query(self):
        query = f'''INSERT INTO TableElementTime
        VALUES ({self.date_of_start}, {self.time_of_start}, {self.period},
                {self.date_of_end}, {self.time_of_end})'''
        return query

    def make_change_query(self):
        pass


class ChangingForm(QDialog, Ui_Dialog):
    def __init__(self, db_con):
        super().__init__()
        self.setupUi(self)
        self.db_con = db_con
        [btn.clicked.connect(self.change_operation) for btn in self.oper_rbtns.buttons()]
        [btn.clicked.connect(self.change_table) for btn in self.tabl_rbtns.buttons()]
        self.commit_btn.clicked.connect(self.commit_data)

        cur = self.db_con.cursor()
        self.is_change_operation = False
        self.types = ['timetable', 'deadline']
        self.types = dict(zip(
            self.types,
            cur.execute("SELECT title FROM Types").fetchall()
        ))
        self.chosen_type = self.types['deadline']
        self.update_data()

    def get_type_id(self):
        cur = self.db_con.cursor()
        return cur.execute(
            f"SELECT id FROM Types WHERE title = '{self.chosen_type[0]}'"
        ).fetchall()[0][0]

    def update_data(self):
        cur = self.db_con.cursor()
        query = f"SELECT title FROM TableElements WHERE type_id = {self.get_type_id()}"
        self.select_cbx.clear()
        for i, item in enumerate(cur.execute(query).fetchall()):
            self.select_cbx.addItem(item[0])

    def change_operation(self):
        if self.oper_rbtns.checkedButton() is self.add_oper_rbtn:
            self.select_cbx.setEditable(False)
            self.commit_btn.setText("Add")
            self.is_change_operation = False
            self.select_cbx.clear()
        else:
            self.select_cbx.setEditable(True)
            self.commit_btn.setText("Change")
            self.is_change_operation = True
            self.update_data()

    def change_table(self):
        if self.sender() is self.dead_tabl_rbtn:
            self.chosen_type = self.types["deadline"]
        else:
            self.chosen_type = self.types["timetable"]
        self.update_data()

    def commit_data(self):
        time_data = [
            self.start_date_edt.date().toPyDate(),  # date_of_start
            self.start_time_edt.time().toPyTime(),  # time_of_start
            self.end_date_edt.date().toPyDate(),  # date_of_end
            self.end_time_edt.time().toPyTime(),  # time_of_end
            int(self.period_days_edt.text())  # period_in_days
        ]
        table_element_time = TableElementTime(*time_data)

        cur = self.db_con.cursor()
        title = self.title_edt.text()
        type_id = self.get_type_id()

        if self.is_change_operation:
            query = f'''
            UPDATE TableElements
            SET title = "{title}", type_id = "{type_id}"
            WHERE title = "{self.select_cbx.currentText()}";'''
            query += table_element_time.make_change_query()
        else:
            query = f"INSERT INTO TableElements(title, type_id) VALUES ('{title}', '{type_id}')"
            query += table_element_time.make_add_query()

        print(query)
        cur.execute(query).fetchall()
        self.db_con.commit()
        self.close()


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db_con = sqlite3.connect("db.db")
        self.show_data()
        self.add_dead_btn.clicked.connect(self.change_data)
        self.add_ttab_btn.clicked.connect(self.change_data)
        self.chg_dead_btn.clicked.connect(self.change_data)
        self.chg_ttab_btn.clicked.connect(self.change_data)
        self.changing_form = ChangingForm(self.db_con)

    def change_data(self):

        self.changing_form.oper_rbtns.buttons()[1].setChecked(True)

        if self.sender() in self.add_btns.buttons():
            self.changing_form.oper_rbtns.buttons()[0].setChecked(True)

        self.changing_form.change_operation()

        self.changing_form.tabl_rbtns.buttons()[1].setChecked(True)
        self.changing_form.chosen_type = self.changing_form.types['deadline']

        if self.sender().parent() != self.dead_btns:
            self.changing_form.tabl_rbtns.buttons()[0].setChecked(True)
            self.changing_form.chosen_type = self.changing_form.types['timetable']

        self.changing_form.show()

    def show_data(self):
        # self.dead_tabl.setColumnCount(5)
        # self.dead_tabl.setRowCount(5)
        # self.dead_tabl.setItem(0, 0, QTableWidgetItem("123123"))
        # self.dead_tabl.resizeColumnsToContents()
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
