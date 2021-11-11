import sqlite3
import sys
from datetime import date, time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog  # , QTableWidgetItem
from main_form import Ui_MainWindow
from data_change_form import Ui_Dialog


class TableElementTime:
    def __init__(self, *args):
        self.date_of_start = args[0]
        self.time_of_start = args[1]
        self.date_of_end = args[2]
        self.time_of_end = args[3]
        self.period = args[4]

    def make_add_query(self, title):
        date_format = "%d%m%Y"
        time_format = "%H%M"
        query = f'''INSERT INTO TableElementTime(table_element_id, date_of_start,
        time_of_start, period, date_of_end, time_of_end)
        VALUES (
        (SELECT id FROM TableElements WHERE title = "{title}"),
        {self.date_of_start.strftime(date_format)}, {self.time_of_start.strftime(time_format)},
        {self.period},
        {self.date_of_end.strftime(date_format)}, {self.time_of_end.strftime(time_format)})'''
        return query

    def make_change_query(self, title):
        return f'''
            UPDATE TableElementTime
            SET date_of_start = "{self.date_of_start}", date_of_end = "{self.date_of_end}",
            period = "{self.period}", date_of_end = "{self.date_of_end}", time_of_end = "{self.time_of_end}"
            WHERE table_element_id = (SELECT id FROM TableElements WHERE title = "{title}")'''


class ChangingForm(QDialog, Ui_Dialog):
    def __init__(self, db_con):
        super().__init__()
        self.setupUi(self)
        self.db_con = db_con
        [btn.clicked.connect(self.change_operation) for btn in self.oper_rbtns.buttons()]
        [btn.clicked.connect(self.change_table) for btn in self.tabl_rbtns.buttons()]
        self.commit_btn.clicked.connect(self.commit_data)
        self.find_btn.clicked.connect(self.update_current_data)

        cur = self.db_con.cursor()
        self.is_change_operation = False
        self.types = ['timetable', 'deadline']
        self.types = dict(zip(
            self.types,
            cur.execute("SELECT title FROM Types").fetchall()
        ))
        self.chosen_type = self.types['deadline']
        self.update_all_data()

    def update_current_data(self):
        cur = self.db_con.cursor()
        query = f'''SELECT * FROM TableElementTime
        WHERE table_element_id = (
        SELECT id FROM TableElements
        WHERE title = "{self.select_cbx.currentText()}"
        )'''
        self.title_edt.setText(self.select_cbx.currentText())
        result = list(map(str, cur.execute(query).fetchall()[0]))
        date_of_start = date(*list(map(int, reversed((result[2][:2], result[2][2:4], result[2][4:])))))
        date_of_end = date(*list(map(int, reversed((result[2][:2], result[2][2:4], result[2][4:])))))
        period = int(result[4])
        time_of_start = time(*list(map(int, (result[5][:2], result[5][2:]))))
        time_of_end = time(*list(map(int, (result[6][:2], result[6][2:]))))

        self.start_date_edt.setDate(date_of_start)
        self.end_date_edt.setDate(date_of_end)
        self.start_time_edt.setTime(time_of_start)
        self.end_time_edt.setTime(time_of_end)
        self.period_days_edt.setValue(period)

    def get_type_id(self):
        cur = self.db_con.cursor()
        return cur.execute(
            f"SELECT id FROM Types WHERE title = '{self.chosen_type[0]}'"
        ).fetchall()[0][0]

    def update_all_data(self):
        cur = self.db_con.cursor()
        query = f"SELECT title FROM TableElements WHERE type_id = {self.get_type_id()}"
        self.select_cbx.clear()
        for i, item in enumerate(cur.execute(query).fetchall()):
            self.select_cbx.addItem(item[0])

    def change_operation(self):
        if self.oper_rbtns.checkedButton() is self.add_oper_rbtn:
            self.commit_btn.setText("Add")
            change = False
        else:
            self.commit_btn.setText("Change")
            change = True

        self.is_change_operation = change
        self.select_cbx.setVisible(change)
        self.find_btn.setVisible(change)
        self.update_all_data()

    def change_table(self):
        if self.sender() is self.dead_tabl_rbtn:
            self.chosen_type = self.types["deadline"]
        else:
            self.chosen_type = self.types["timetable"]
        self.update_all_data()

    def commit_data(self):
        time_data = [
            self.start_date_edt.date().toPyDate(),  # date_of_start
            self.start_time_edt.time().toPyTime(),  # time_of_start
            self.end_date_edt.date().toPyDate(),  # date_of_end
            self.end_time_edt.time().toPyTime(),  # time_of_end
            int(self.period_days_edt.text())  # period
        ]
        table_element_time = TableElementTime(*time_data)

        cur = self.db_con.cursor()
        title = self.title_edt.text()
        type_id = self.get_type_id()

        if self.is_change_operation:
            query_1 = f'''
            UPDATE TableElements
            SET title = "{title}", type_id = "{type_id}"
            WHERE title = "{self.select_cbx.currentText()}"'''
            query_2 = table_element_time.make_change_query(title)
        else:
            query_1 = f'''
            INSERT INTO TableElements(title, type_id)
            VALUES ("{title}", "{type_id}")'''
            query_2 = table_element_time.make_add_query(title)

        cur.execute(query_1).fetchall()
        cur.execute(query_2).fetchall()
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
