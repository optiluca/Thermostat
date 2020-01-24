import sqlite3


class DatabaseLoggingService:
    def __init__(self):
        self.db_connection = self.setup_db(create_table=True)
        pass

    def add_row_to_db(self, feedbackTemp, targetTemp, ambientTemp, boilerActive):
        pass

    def setup_db(db_file='Thermostat.db', create_table=False):
        # Connect
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        if create_table:
            # Create table
            create_table_sql = """CREATE TABLE IF NOT EXISTS stats (
                                    time integer PRIMARY KEY,
                                    sensor_temperature real NOT NULL,
                                    target_temperature real NOT NULL,
                                    outside_temperature real,
                                    boiler_on integer NOT NULL
                                );"""

            try:
                c = conn.cursor()
                c.execute(create_table_sql)
            except Error as e:
                print(e)

        return conn

    def add_row_to_db(conn, time=None, sensor_temperature=None, target_temperature=None, outside_temperature=None,
                      boiler_on=None):
        row = (time, sensor_temperature, target_temperature, boiler_on, outside_temperature)
        sql = ''' INSERT INTO stats(time,sensor_temperature,target_temperature,boiler_on,outside_temperature)
                  VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, row)
        conn.commit()
        return cur.lastrowid

    def select_data_in_range(conn, t_start, t_end):
        cur = conn.cursor()
        cur.execute("SELECT time,sensor_temperature,target_temperature,boiler_on FROM stats WHERE time>=? AND time<?",
                    (t_start, t_end))

        times = []
        sensor_temps = []
        target_temps = []
        boiler_ons = []
        rows = cur.fetchall()
        for row in rows:
            times.append(row[0])
            sensor_temps.append(row[1])
            target_temps.append(row[2])
            boiler_ons.append(row[3])

        return times, sensor_temps, target_temps, boiler_ons