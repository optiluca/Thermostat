import time
import numpy as np
from scipy import optimize
from utils import setup_logger, select_when_flag_true
from Models.House import House
from Services.DatabaseServices import ThermostatDatabaseService, HouseDatabaseService


class HouseModelFittingService:
    def __init__(self):
        self.logger = setup_logger('HouseModelFitting.log')
        self.house_database_service = HouseDatabaseService(False)
        self.thermostat_database_service = ThermostatDatabaseService(True)

        self.radiator_temp = 52.0  # TODO this service should have a House which it fits and clones to Thermostat
        self.k1_best_fit = None
        self.k2_best_fit = None

    def fit_house_model(self, boiler_active):
        house_model = None

        if boiler_active:
            k = self._update_k1_best_fit()
            is_k1_latest_fit = True
            text_body = 'Best Fit K1: {}, Best Fit K2: {}, Latest Fit K1: {}'
        else:
            k = self._update_k2_best_fit()
            is_k1_latest_fit = False
            text_body = 'Best Fit K1: {}, Best Fit K2: {}, Latest Fit K2: {}'

        if self.k1_best_fit and self.k2_best_fit:
            house_model = House(self.k1_best_fit, self.k2_best_fit)

            status_string = text_body.format(house_model.k1, house_model.k2, k)
            self.logger.info(status_string)

        now = int(time.time())
        self.house_database_service.add_row_to_db(now, self.k1_best_fit, self.k2_best_fit, k, is_k1_latest_fit)
        return house_model

    def _update_k1_best_fit(self):
        new_k = self._fit_k1()
        if new_k:
            self.k1_best_fit = self._update_best_fit(new_k, self.k1_best_fit)
        return new_k

    def _update_k2_best_fit(self):
        new_k = self._fit_k2()
        if new_k:
            self.k2_best_fit = self._update_best_fit(new_k, self.k2_best_fit)
        return new_k

    def _fit_k1(self):
        new_k1 = None
        try:
            sampled_times, sampled_temps, average_ambient_temp = self._get_data_for_fitting(False)

            def f_boiler_off(t, initial_temp, k1, ambient_temp):
                # TODO get lambda from House
                temp = ambient_temp + (initial_temp - ambient_temp) * np.exp(-k1 * t)
                return temp

            p_opt = optimize.curve_fit(
                lambda t, initial_temp, k1: f_boiler_off(t, initial_temp, k1, average_ambient_temp),
                sampled_times, sampled_temps,
                bounds=((10, 1e-7), (20, 1e-5)))

            new_k1 = p_opt[0][1]
        except Exception as e:
            print(e)
        return new_k1

    def _fit_k2(self):
        new_k2 = None
        try:
            if self.k1_best_fit is None:
                raise Exception("k1 is currently None - cannot fit k2 yet")

            sampled_times, sampled_temps, average_ambient_temp = self._get_data_for_fitting(True)

            def f_boiler_on(t, initial_temp, k1, k2, ambient_temp, radiator_temp):
                # TODO get lambda from House
                equilibrium_temp = (k1 * ambient_temp + k2 * radiator_temp) / (k1 + k2)
                temp = equilibrium_temp + (initial_temp - equilibrium_temp) * np.exp(-(k1 + k2) * t)
                return temp

            p_opt = optimize.curve_fit(
                lambda t, initial_temp, k2: f_boiler_on(t, initial_temp, self.k1_best_fit, k2,
                                                        average_ambient_temp, self.radiator_temp),
                sampled_times, sampled_temps,
                bounds=((10, 1e-7), (20, 1e-5)))

            new_k2 = p_opt[0][1]
        except Exception as e:
            print(e)
        return new_k2

    def _get_data_for_fitting(self, boiler_active):
        end_time = int(time.time())
        start_time = end_time - 3600 * 24

        times, sensor_temps, target_temps, boiler_ons = \
            self.thermostat_database_service.select_data_in_range(start_time, end_time)

        times = np.array(times)
        temps = np.array(sensor_temps)
        boiler_ons = np.array(boiler_ons, dtype=np.bool)

        average_ambient_temp = 3  # TODO from DB

        if boiler_active:
            sampled_times = select_when_flag_true(times, boiler_ons)
            sampled_temps = select_when_flag_true(temps, boiler_ons)
        else:
            sampled_times = select_when_flag_true(times, np.logical_not(boiler_ons))
            sampled_temps = select_when_flag_true(temps, np.logical_not(boiler_ons))

        sampled_times = sampled_times[0]
        sampled_times = sampled_times - sampled_times[0]

        sampled_temps = sampled_temps[0]

        return sampled_times, sampled_temps, average_ambient_temp

    @staticmethod
    def _update_best_fit(latest_fit, current_best_fit):
        # e.g. confidence weighted average
        return current_best_fit
