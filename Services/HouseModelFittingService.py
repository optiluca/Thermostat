import time
from utils import setup_logger
from Models.House import House
from Services.DatabaseServices import ThermostatDatabaseService, HouseDatabaseService


class HouseModelFittingService:
    def __init__(self):
        self.logger = setup_logger('HouseModelFitting.log')
        self.house_database_service = HouseDatabaseService(False)
        self.thermostat_database_service = ThermostatDatabaseService(True)

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
        self.k1_best_fit = self._update_best_fit(new_k, self.k1_best_fit)
        return new_k

    def _update_k2_best_fit(self):
        new_k = self._fit_k2()
        self.k2_best_fit = self._update_best_fit(new_k, self.k2_best_fit)
        return new_k

    def _fit_k1(self):
        return 0

    def _fit_k2(self):
        return 0

    def _update_best_fit(self, latest_fit, current_best_fit):
        # e.g. confidence weighted average
        return current_best_fit
