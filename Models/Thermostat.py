from Services import AmbientTemperatureService as ATS
from Services import BoilerActuationService as BAS
from Services import TargetTemperatureService as TTS
from Services import TemperatureControlService as TCS
from Services import TemperatureMeasurementService as TMS


class Thermostat:
    def __init__(self, config):
        self.isAlive = True

        self.boilerActive = False
        self.targetTemp = None
        self.feedbackTemp = None
        self.ambientTemp = None

        self.ambientTemperatureService = ATS.AmbientTemperatureService(config)
        self.boilerActuationService = BAS.BoilerActuationService()
        self.targetTemperatureService = TTS.TargetTemperatureService(config)
        self.temperatureControlService = TCS.TemperatureControlService()
        self.temperatureMeasurementService = TMS.TemperatureMeasurementService()

    def update(self):
        try:
            self.try_update_temperatures()
            self.__try_control_temperature()
            self.isAlive = True
        except Exception as e:
            print(e)
            self.isAlive = False

    def kill(self):
        try:
            self.__try_set_boiler(False)
            self.isAlive = False
        except Exception as e:
            print(e)

    def try_update_temperatures(self):
        try:
            self.__try_get_feedback_temperature()
            self.__try_get_target_temperature()
            self.__try_get_ambient_temperature()
            return True
        except Exception as e:
            print(e)
            return False

    def set_parameter(self, parameter, value):
        if parameter in ['morning_beginning', 'morning_end',
                         'evening_beginning', 'evening_end',
                         'night_temp', 'day_temp', 'away_temp']:
            setattr(self.targetTemperatureService, parameter, value)

    def __try_get_feedback_temperature(self):
        feedbackTemp = self.temperatureMeasurementService.try_get_feedback_temperature()
        if not feedbackTemp:
            raise Exception("Unable to measure feedback temperature")
        self.feedbackTemp = feedbackTemp

    def __try_get_target_temperature(self):
        targetTemp = self.targetTemperatureService.try_get_target_temp()
        if not targetTemp:
            raise Exception("Unable to set target temperature")
        self.targetTemp = targetTemp

    def __try_get_ambient_temperature(self):
        ambientTemp = self.ambientTemperatureService.try_get_ambient_temperature()
        if not ambientTemp:
            raise Exception("Unable to get ambient temperature")
        self.ambientTemp = ambientTemp

    def __try_control_temperature(self):
        boilerActive = self.temperatureControlService.try_compute_boiler_activation_signal(self.targetTemp,
                                                                                           self.feedbackTemp)
        if boilerActive is None:
            raise Exception("Unable to compute boiler actuation signal")

        if boilerActive is not self.boilerActive:
            self.__try_set_boiler(boilerActive)

    def __try_set_boiler(self, boilerActive):
        isSuccess = self.boilerActuationService.try_actuate_boiler(boilerActive)
        if isSuccess is None:
            raise Exception("Unable to actuate boiler")

        self.boilerActive = boilerActive
