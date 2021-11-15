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
        "{self.date_of_start.strftime(date_format)}", "{self.time_of_start.strftime(time_format)}",
        {self.period},
        "{self.date_of_end.strftime(date_format)}", "{self.time_of_end.strftime(time_format)}")'''
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
