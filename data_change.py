from datetime import date, time
from table_element_time import TableElementTime
from PyQt5.QtWidgets import QDialog
from data_change_ui import Ui_Dialog as UI_Data_Change


class ChangingForm(QDialog, UI_Data_Change):
    def __init__(self, db_con, viewer, main):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('Time Manager')
        self.db_con = db_con
        self.viewer = viewer
        self.main = main
        [btn.clicked.connect(self.change_operation) for btn in self.oper_rbtns.buttons()]
        [btn.clicked.connect(self.change_table) for btn in self.tabl_rbtns.buttons()]
        self.commit_btn.clicked.connect(self.commit_data)
        self.find_btn.clicked.connect(self.update_current_data)

        cur = self.db_con.cursor()
        self.is_change_operation = False
        self.is_delete = False
        self.types = ['timetable', 'deadline']
        self.types = dict(zip(
            self.types,
            cur.execute("SELECT title FROM Types").fetchall()
        ))
        if self.dead_tabl_rbtn.isChecked():
            self.chosen_type = self.types['deadline']
        else:
            self.chosen_type = self.types["timetable"]
        self.update_all_data()

    def close(self):
        self.viewer.update_data()
        self.main.show_data()
        super(ChangingForm, self).close()

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

    def show_change_stuff(self):
        self.start_time_edt.setVisible(not self.is_delete)
        self.start_date_edt.setVisible(not self.is_delete)
        self.start_txt.setVisible(not self.is_delete)
        self.end_date_edt.setVisible(not self.is_delete)
        self.end_time_edt.setVisible(not self.is_delete)
        self.end_txt.setVisible(not self.is_delete)
        if not self.chosen_type == self.types["deadline"]:
            self.period_txt.setVisible(not self.is_delete)
            self.period_days_edt.setVisible(not self.is_delete)
        if self.is_delete:
            self.select_cbx.setVisible(True)
            self.find_btn.setVisible(True)
            self.commit_btn.setText("Delete")

    def change_operation(self):
        if self.oper_rbtns.checkedButton() is self.add_oper_rbtn:
            self.commit_btn.setText("Add")
            change = False
        else:
            self.commit_btn.setText("Change")
            change = True

        if self.oper_rbtns.checkedButton() is self.del_oper_rbtn:
            delete = True
        else:
            delete = False

        if not delete:
            self.is_change_operation = change
            self.select_cbx.setVisible(change)
            self.find_btn.setVisible(change)
            self.update_all_data()
            self.is_delete = False
            self.show_change_stuff()
        else:
            self.is_delete = True

        self.show_change_stuff()

    def change_table(self):
        if self.tabl_rbtns.checkedButton() is self.dead_tabl_rbtn:
            time_table = False
            self.chosen_type = self.types["deadline"]
        else:
            self.chosen_type = self.types["timetable"]
            time_table = True
        if not self.is_delete:
            self.period_days_edt.setVisible(time_table)
            self.period_txt.setVisible(time_table)
        self.update_all_data()

    def commit_data(self):
        cur = self.db_con.cursor()
        title = self.title_edt.text()
        type_id = self.get_type_id()
        if self.is_delete:
            query_1 = f'''
                        DELETE FROM TableElementTime
                        WHERE table_element_id = (
                        SELECT id FROM TableElements
                        WHERE title = "{self.title_edt}")'''
            query_2 = f'''
                        DELETE FROM TableElements
                        WHERE title = "{self.title_edt}"'''
        else:
            time_data = [
                self.start_date_edt.date().toPyDate(),  # date_of_start
                self.start_time_edt.time().toPyTime(),  # time_of_start
                self.end_date_edt.date().toPyDate(),  # date_of_end
                self.end_time_edt.time().toPyTime(),  # time_of_end
                self.period_days_edt.value()  # period
            ]
            table_element_time = TableElementTime(*time_data)

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
