from datetime import datetime, timedelta
from calendar import monthrange
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from viewer_ui import Ui_Dialog as UI_Viewer
from data_change import ChangingForm


class Viewer(QDialog, UI_Viewer):
    def __init__(self, db_con, main):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('Time Manager')
        self.db_con = db_con

        self.is_deadline = False
        self.ttab_rbtn.setChecked(True)
        self.changing_form = ChangingForm(self.db_con, self, main)

        self.today = datetime.today()
        self.today.replace(self.today.year, self.today.month, 1)
        self.back_month_btn.clicked.connect(self.change_month)
        self.forward_month_btn.clicked.connect(self.change_month)
        self.month_txt.setText(self.today.strftime("%Y.%m"))
        [btn.clicked.connect(self.update_data) for btn in self.type_bgp.buttons()]

        self.change_btn.clicked.connect(self.open_data_changer)
        self.update_data()

    def update_data(self):
        self.viewer_tbl.clear()
        cur = self.db_con.cursor()
        start_day, number_of_days = monthrange(self.today.year, self.today.month)
        self.rows = (start_day + number_of_days) // 7 + min(1, start_day + number_of_days % 7)
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

        query = f'''SELECT TableElements.title, TableElementTime.date_of_start,
                        TableElementTime.date_of_end, TableElementTime.period FROM TableElements
                        JOIN TableElementTime ON TableElementTime.table_element_id = TableElements.id
                        WHERE type_id = '''
        if self.type_bgp.checkedButton() is self.ttab_rbtn:
            query += "1"
            result = cur.execute(query).fetchall()
            table = [[] for _ in range(number_of_days)]
            for table_element in result:
                date_of_end = datetime(*list(
                    map(int, reversed((table_element[2][:2], table_element[2][2:4], table_element[2][4:])))))
                if date_of_end >= datetime(self.today.year, self.today.month, 1):
                    title = table_element[0]
                    date_of_start = datetime(*list(
                        map(int, reversed((table_element[1][:2], table_element[1][2:4], table_element[1][4:])))))
                    period = table_element[3]
                    new_day = date_of_start
                    if period != 0:
                        while new_day <= date_of_end:
                            if new_day.month == self.today.month:
                                table[new_day.day - 1].append(title)
                            new_day = new_day + timedelta(days=period)
                    else:
                        if new_day.month == self.today.month:
                            table[new_day.day - 1].append(title)
        else:
            query += "2"
            result = cur.execute(query).fetchall()
            table = [[] for _ in range(number_of_days)]
            for table_element in result:
                title = table_element[0]
                date_of_end = datetime(*list(
                    map(int, reversed((table_element[2][:2], table_element[2][2:4], table_element[2][4:])))))
                if datetime(self.today.year, self.today.month, date_of_end.day) == date_of_end:
                    table[date_of_end.day - 1].append(title)
        for i in range(number_of_days):
            if table[i]:
                item = QTableWidgetItem("\n".join(table[i]))
            else:
                item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(4)
            self.viewer_tbl.setItem((start_day + i) // 7, (start_day + i) % 7, item)

    def change_month(self):
        if self.sender() is self.back_month_btn:
            self.today = self.today + timedelta(days=-(monthrange(self.today.year, self.today.month))[1])
        else:
            self.today = self.today + timedelta(days=(monthrange(self.today.year, self.today.month))[1])
        self.month_txt.setText(self.today.strftime("%Y.%m"))
        self.update_data()

    def open_data_changer(self):

        self.changing_form.oper_rbtns.buttons()[1].setChecked(True)

        self.changing_form.change_operation()

        self.changing_form.tabl_rbtns.buttons()[1].setChecked(True)
        self.changing_form.chosen_type = self.changing_form.types['deadline']
        if not self.dead_rbtn.isChecked():
            self.changing_form.tabl_rbtns.buttons()[0].setChecked(True)
            self.changing_form.chosen_type = self.changing_form.types['timetable']

        self.changing_form.change_table()
        self.changing_form.show()
