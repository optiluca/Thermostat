import sqlite3
import time
from scipy import optimize
import matplotlib.pyplot as plt
import numpy as np


def select_when_flag_true(a, boo):
    indices = np.nonzero(boo[1:] != boo[:-1])[0] + 1
    b = np.split(a, indices)
    b = b[0::2] if boo[0] else b[1::2]
    return b


def setup_db(db_file='Thermostat.db', create_table=False):
    # Connect
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
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
        except sqlite3.Error as e:
            print(e)

    return conn


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


conn = setup_db(create_table=False, db_file='../Thermostat.db')

t_end = int(time.time())

t_start = t_end - 3600 * 24

times, sensor_temps, target_temps, boiler_ons = select_data_in_range(conn, t_start, t_end)

t = np.array(times)
T = np.array(sensor_temps)
b_boiler = np.array(boiler_ons, dtype=np.bool)

'''
times = [datetime.datetime.fromtimestamp(x) for x in t]
plt.plot(times, T)
plt.plot(times, b_boiler+14)
plt.show()
'''

T_out = 0  # wild estimate

t_split = select_when_flag_true(t, np.logical_not(b_boiler))
T_split = select_when_flag_true(T, np.logical_not(b_boiler))

idx_fit = [0]

t_to_fit = t_split[0]
t_to_fit = t_to_fit - t_to_fit[0]

T_to_fit = T_split[0]

plt.plot(t_to_fit, T_to_fit)


def f_boiler_off(t, T_0, k1, T_amb):
    T = T_amb + (T_0 - T_amb) * np.exp(-k1 * t)
    return T


p_opt = optimize.curve_fit(lambda t, T_0, k1: f_boiler_off(t, T_0, k1, T_out), t_to_fit, T_to_fit, bounds=((10, 1e-7), (20, 1e-5)))

y_fitted = f_boiler_off(t_to_fit, p_opt[0][0], p_opt[0][1], T_out)

# y_fitted = f_boiler_off(t_to_fit, 16.3, 4.5e-6, T_out)

plt.plot(t_to_fit, y_fitted)
plt.show()
