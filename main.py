import sqlite3
import sys
from datetime import date, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from main_form import Ui_TimeTable
from viewer import Viewer


class Main(QMainWindow, Ui_TimeTable):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db_con = sqlite3.connect("db.db")
        self.viewer = Viewer(self.db_con, self)

        self.setWindowTitle('Time Manager')
        self.today = date.today() + timedelta(days=-1)
        self.change_date()
        self.dead_tabl.setColumnCount(2)
        self.ttab_tabl.setColumnCount(2)
        self.show_data()
        self.view_btn.clicked.connect(self.open_viewer)
        self.date_back_btn.clicked.connect(self.change_date)
        self.date_forw_btn.clicked.connect(self.change_date)

    def change_date(self):
        if self.sender() is self.date_back_btn:
            self.today = self.today + timedelta(days=-1)
        else:
            self.today = self.today + timedelta(days=1)
        self.date_txt.setText(self.today.strftime("%d.%m.%Y"))
        self.show_data()

    def open_viewer(self):
        self.viewer.show()

    def show_data(self):
        cur = self.db_con.cursor()

        time_table_list = []
        query = f'''SELECT TableElements.title, TableElementTime.date_of_start,
                            TableElementTime.date_of_end, TableElementTime.time_of_start,
                            TableElementTime.time_of_end, TableElementTime.period FROM TableElements
                            JOIN TableElementTime ON TableElementTime.table_element_id = TableElements.id
                            WHERE TableElements.type_id = 1'''
        result = cur.execute(query).fetchall()
        for res in result:
            date_of_end = date(*list(map(int, reversed((res[2][:2], res[2][2:4], res[2][4:])))))
            if date_of_end >= self.today:
                date_of_start = date(*list(map(int, reversed((res[1][:2], res[1][2:4], res[1][4:])))))
                new_date = date(*list(map(int, reversed((res[1][:2], res[1][2:4], res[1][4:])))))
                period = res[5]
                if period != 0:
                    while new_date < date_of_end:
                        if self.today == new_date:
                            time_table_list.append(res)
                        new_date = new_date + timedelta(days=period)
                else:
                    if self.today == new_date:
                        time_table_list.append(res)

        self.ttab_tabl.setRowCount(len(time_table_list))
        for i, time_table_el in enumerate(time_table_list):
            self.ttab_tabl.setItem(i, 0, QTableWidgetItem(time_table_el[0]))
            table_element_time = f"{time_table_el[3][:2]}:{time_table_el[3][2:]}-" +\
                f"{time_table_el[4][:2]}:{time_table_el[4][2:]}"
            self.ttab_tabl.setItem(i, 1, QTableWidgetItem(table_element_time))
        self.ttab_tabl.resizeColumnsToContents()

        dead_line_list = []
        query = f'''SELECT TableElements.title, TableElementTime.date_of_start,
                    TableElementTime.date_of_end, TableElementTime.time_of_start,
                    TableElementTime.time_of_end, TableElementTime.period FROM TableElements
                    JOIN TableElementTime ON TableElementTime.table_element_id = TableElements.id
                    WHERE TableElements.type_id = 2'''
        result = cur.execute(query).fetchall()
        for res in result:
            date_of_end = date(*list(map(int, reversed((res[2][:2], res[2][2:4], res[2][4:])))))
            if date_of_end >= self.today:
                dead_line_list.append(res)

        self.dead_tabl.setRowCount(len(dead_line_list))
        for i, dead_line_el in enumerate(dead_line_list):
            self.dead_tabl.setItem(i, 0, QTableWidgetItem(dead_line_el[0]))
            table_element_time = f"{dead_line_el[4][:2]}:{dead_line_el[4][2:]}"
            self.dead_tabl.setItem(i, 1, QTableWidgetItem(table_element_time))
        self.dead_tabl.resizeColumnsToContents()


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
