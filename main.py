import sqlite3
import sys
from datetime import date, datetime, time, timedelta
from calendar import monthrange

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem
from main_form import Ui_MainWindow
from data_change_form import Ui_Dialog as UI_Data_Change
from viewer import Ui_Dialog as UI_Viewer


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
        date_format = "%d%m%Y"
        time_format = "%H%M"
        query = f'''
            UPDATE TableElementTime
            SET date_of_start = "{self.date_of_start.strftime(date_format)}",
            date_of_end = "{self.date_of_end.strftime(date_format)}",
            period = "{self.period}",
            time_of_start = "{self.time_of_start.strftime(time_format)}",
            time_of_end = "{self.time_of_end.strftime(time_format)}"
            WHERE table_element_id = (SELECT id FROM TableElements WHERE title = "{title}")'''
        return query


class ChangingForm(QDialog, UI_Data_Change):
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
        date_of_end = date(*list(map(int, reversed((result[3][:2], result[3][2:4], result[3][4:])))))
        period = int(result[4])
        time_of_start = time(*list(map(int, (result[5][:-2], result[5][-2:]))))
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
        if self.tabl_rbtns.checkedButton() is self.dead_tabl_rbtn:
            time_table = False
            self.chosen_type = self.types["deadline"]
        else:
            self.chosen_type = self.types["timetable"]
            time_table = True
        self.period_days_edt.setVisible(time_table)
        self.period_txt.setVisible(time_table)
        self.update_all_data()

    def commit_data(self):
        time_data = [
            self.start_date_edt.date().toPyDate(),  # date_of_start
            self.start_time_edt.time().toPyTime(),  # time_of_start
            self.end_date_edt.date().toPyDate(),  # date_of_end
            self.end_time_edt.time().toPyTime(),  # time_of_end
            self.period_days_edt.value()  # period
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


class Viewer(QDialog, UI_Viewer):
    def __init__(self, db_con):
        super().__init__()
        self.setupUi(self)
        self.db_con = db_con

        self.changing_form = ChangingForm(self.db_con)

        self.today = datetime.today()
        self.month_txt.setText(str(self.today))

        self.change_btn.clicked.connect(self.open_data_changer)
        # self.back_month_btn.clicked.connect(self.change_month)
        # self.forward_month_btn.clicked.connect(self.change_month)
        self.update_data()

    def update_data(self):
        cur = self.db_con.cursor()
        start_day, number_of_days = monthrange(self.today.year, self.today.month)

        self.rows = number_of_days // 7 + min(1, number_of_days % 7)
        self.row_height = 65
        self.columns = 7
        self.column_width = 76
        self.week_days = (
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        )
        self.viewer_tbl.setColumnCount(self.columns)
        self.viewer_tbl.setHorizontalHeaderLabels(self.week_days)
        self.viewer_tbl.setRowCount(self.rows)
        for i in range(self.rows):
            self.viewer_tbl.setRowHeight(i, self.row_height)
        for i in range(self.columns):
            self.viewer_tbl.setColumnWidth(i, self.column_width)

        for i in range(number_of_days):
            self.viewer_tbl.setItem(i // 7, (start_day + i) % 7, QTableWidgetItem(str(i + 1)))

        query = f'''SELECT TableElements.title, TableElementTime.date_of_start,
                    TableElementTime.date_of_end, TableElementTime.time_of_start,
                    TableElementTime.time_of_end, TableElementTime.period FROM TableElements
                    JOIN TableElementTime ON TableElementTime.table_element_id = TableElements.id
                    WHERE type_id = 1'''
        result = cur.execute(query).fetchall()
        for table_element in result:
            title = table_element[0]
            date_of_start = datetime(*list(
                map(int, reversed((table_element[1][:2], table_element[1][2:4], table_element[1][4:])))))
            date_of_end = datetime(*list(
                map(int, reversed((table_element[2][:2], table_element[2][2:4], table_element[2][4:])))))
            time_of_start = table_element[3]
            time_of_end = table_element[4]
            period = table_element[5]
            if self.today < date_of_end:
                # print(table_element, date_of_end)
                pass

    def change_month(self):
        change = -1
        if self.sender() is self.forward_month_btn:
            change = 1
        # self.today.replace()
        self.month_txt.setText(str(self.today))

    def open_data_changer(self):

        self.changing_form.oper_rbtns.buttons()[1].setChecked(True)
        # if self.sender() in self.add_btns.buttons():
        #     self.changing_form.oper_rbtns.buttons()[0].setChecked(True)

        self.changing_form.change_operation()

        self.changing_form.tabl_rbtns.buttons()[1].setChecked(True)
        self.changing_form.chosen_type = self.changing_form.types['deadline']
        # if self.sender().parent() != self.dead_btns:
        #     self.changing_form.tabl_rbtns.buttons()[0].setChecked(True)
        #     self.changing_form.chosen_type = self.changing_form.types['timetable']

        self.changing_form.change_table()

        self.changing_form.show()


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db_con = sqlite3.connect("db.db")
        self.viewer = Viewer(self.db_con)

        self.tomorrow = date.today() + timedelta(days=1)
        self.dead_tabl.setColumnCount(1)
        self.ttab_tabl.setColumnCount(2)

        self.show_data()
        self.view_btn.clicked.connect(self.open_viewer)
        self.refresh_btn.clicked.connect(self.show_data)

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
            if date_of_end >= self.tomorrow:
                date_of_start = date(*list(map(int, reversed((res[1][:2], res[1][2:4], res[1][4:])))))
                new_date = date(*list(map(int, reversed((res[1][:2], res[1][2:4], res[1][4:])))))
                period = res[5]
                while new_date < date_of_end:
                    if self.tomorrow == new_date:
                        time_table_list.append(res)
                    new_date = new_date + timedelta(days=period)

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
            if date_of_end >= self.tomorrow:
                dead_line_list.append(res)

        self.dead_tabl.setRowCount(len(dead_line_list))
        for i, dead_line_el in enumerate(dead_line_list):
            self.dead_tabl.setItem(i, 0, QTableWidgetItem(dead_line_el[0]))
        self.dead_tabl.resizeColumnsToContents()

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
