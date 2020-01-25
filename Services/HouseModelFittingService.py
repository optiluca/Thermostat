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
            text_body = 'Latest Fit K1: {}, Best Fit K1: {}, Best Fit K2: {}'
        else:
            k = self._update_k2_best_fit()
            text_body = 'Latest Fit K2: {}, Best Fit K1: {}, Best Fit K2: {}'

        if self.k1_best_fit and self.k2_best_fit:
            house_model = House(self.k1_best_fit, self.k2_best_fit)

            status_string = text_body.format(k, house_model.k1, house_model.k2)
            self.logger.info(status_string)

        return house_model

    def _update_k1_best_fit(self):
        # read data from database
        # fit latest K1
        # update best K1
        return 0

    def _update_k2_best_fit(self):
        # read data from database
        # fit latest K2 given best K1
        # update best K2
        return 0
