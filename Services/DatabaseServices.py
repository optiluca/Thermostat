from Factories.DatabaseFactory import create_thermostat_database, create_house_database


class ThermostatDatabaseService:
    def __init__(self, read_only):
        # In principle could have channel list in ThermostatDatabaseService
        # Pass channel list to generic create_database method in DatabaseFactory
        # Private functions for generating sql from channel list would live in DatabaseFactory
        self.database = create_thermostat_database(read_only)

    def add_row_to_db(self, time=None, sensor_temperature=None, target_temperature=None, outside_temperature=None,
                      boiler_on=None):
        row = (time, sensor_temperature, target_temperature, boiler_on, outside_temperature)
        return self.database.add_row_to_db(row)

    def select_data_in_range(self, t_start, t_end):
        rows = self.database.select_data_in_range(t_start, t_end)

        times = []
        sensor_temps = []
        target_temps = []
        boiler_ons = []
        ambient_temps = []

        for row in rows:
            times.append(row[0])
            sensor_temps.append(row[1])
            target_temps.append(row[2])
            boiler_ons.append(row[3])
            ambient_temps.append(row[4])

        return times, sensor_temps, target_temps, boiler_ons, ambient_temps


class HouseDatabaseService:
    def __init__(self, read_only):
        # In principle could have channel list in HouseDatabaseService
        # Pass channel list to generic create_database method in DatabaseFactory
        # Private functions for generating sql from channel list would live in DatabaseFactory
        self.database = create_house_database(read_only)

    def add_row_to_db(self, time=None, k1_best_fit=None, k2_best_fit=None,
                      k_latest_fit=None, is_k1_latest_fit=None):
        row = (time, k1_best_fit, k2_best_fit, k_latest_fit, is_k1_latest_fit)
        return self.database.add_row_to_db(row)

    def select_data_in_range(self, t_start, t_end):
        rows = self.database.select_data_in_range(t_start, t_end)

        times = []
        k1_best_fit = []
        k2_best_fit = []
        k_latest_fit = []
        is_k1_latest_fit = []
        for row in rows:
            times.append(row[0])
            k1_best_fit.append(row[1])
            k2_best_fit.append(row[2])
            k_latest_fit.append(row[3])
            is_k1_latest_fit.append(row[4])

        return times, k1_best_fit, k2_best_fit, k_latest_fit, is_k1_latest_fit
