import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self, read_only, db_file, sql_create, sql_read, sql_write):
        self.db_file = db_file
        self.sql_read = sql_read
        self.sql_write = sql_write

        if read_only:
            self.db_connection = None
        else:
            self.db_connection = self._create_db(sql_create)

    def add_row_to_db(self, row):
        if self.db_connection:
            cur = self.db_connection.cursor()
            cur.execute(self.sql_write, row)
            self.db_connection.commit()
            return cur.lastrowid

    def select_data_in_range(self, t_start, t_end):
        # Can't use main connection as it's in a different thread!
        conn = self._connect_to_db()
        cur = conn.cursor()
        cur.execute(self.sql_read, (t_start, t_end))
        return cur.fetchall()

    def _create_db(self, sql_create):
        # Connect
        conn = self._connect_to_db()

        if conn:
            try:
                c = conn.cursor()
                c.execute(sql_create)
            except Error as e:
                print(e)
        return conn

    def _connect_to_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        return conn
