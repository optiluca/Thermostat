from Models.House import House

class HouseModelFittingService:
    def __init__(self, database_logging_service):
        self.K1_best_fit = None
        self.K2_best_fit = None
        self.database_logging_service = database_logging_service

    def update_K1_best_fit(self):
        # read data from database
        # fit latest K1
        # update best K1
        pass

    def update_K2_best_fit(self):
        # read data from database
        # fit latest K2 given best K1
        # update best K2
        pass

    def create_house_model(self):
        house_model = None

        if self.K1_best_fit and self.K2_best_fit:
            house_model = House(self.K1_best_fit, self.K2_best_fit)

        return house_model