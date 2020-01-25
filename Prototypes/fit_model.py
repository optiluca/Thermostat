import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
from utils import select_when_flag_true
from scipy import optimize
from Services.DatabaseServices import ThermostatDatabaseService

t_end = int(time.time())
t_start = t_end - 3600 * 24

thermostat_database = ThermostatDatabaseService(True)

times, sensor_temps, target_temps, boiler_ons = thermostat_database.select_data_in_range(t_start, t_end)

t = np.array(times)
T = np.array(sensor_temps)
b_boiler = np.array(boiler_ons, dtype=np.bool)

times = [datetime.datetime.fromtimestamp(x) for x in t]
plt.plot(times, T)
plt.plot(times, b_boiler + 14)
plt.show()

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


p_opt = optimize.curve_fit(lambda t, T_0, k1: f_boiler_off(t, T_0, k1, T_out), t_to_fit, T_to_fit,
                           bounds=((10, 1e-7), (20, 1e-5)))

y_fitted = f_boiler_off(t_to_fit, p_opt[0][0], p_opt[0][1], T_out)

# y_fitted = f_boiler_off(t_to_fit, 16.3, 4.5e-6, T_out)

plt.plot(t_to_fit, y_fitted)
plt.show()
