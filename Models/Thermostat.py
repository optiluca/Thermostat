from Services.AmbientTemperatureService import AmbientTemperatureService
from Services.BoilerActuationService import BoilerActuationService
from Services.TargetTemperatureService import TargetTemperatureService
from Services.TemperatureControlService import TemperatureControlService
from Services.TemperatureMeasurementService import TemperatureMeasurementService


class Thermostat:
    def __init__(self, config):
        self.is_alive = True

        self.boiler_active = False
        self.target_temp = None
        self.feedback_temp = None
        self.ambientTemp = None

        self.ambientTemperatureService = AmbientTemperatureService(config)
        self.boilerActuationService = BoilerActuationService()
        self.targetTemperatureService = TargetTemperatureService(config)
        self.temperatureControlService = TemperatureControlService()
        self.temperatureMeasurementService = TemperatureMeasurementService()

    def update(self):
        try:
            self.try_update_temperatures()
            self._try_control_temperature()
            self.is_alive = True
        except Exception as e:
            print(e)
            self.is_alive = False

    def kill(self):
        try:
            self._try_set_boiler(False)
            self.is_alive = False
        except Exception as e:
            print(e)

    def try_update_temperatures(self):
        try:
            self._try_get_feedback_temperature()
            self._try_get_target_temperature()
            self._try_get_ambient_temperature()
            return True
        except Exception as e:
            print(e)
            return False

    def set_parameter(self, parameter, value):
        if parameter in ['morning_beginning', 'morning_end',
                         'evening_beginning', 'evening_end',
                         'night_temp', 'day_temp', 'away_temp']:
            setattr(self.targetTemperatureService, parameter, value)

    def _try_get_feedback_temperature(self):
        feedback_temp = self.temperatureMeasurementService.try_get_feedback_temperature()
        if not feedback_temp:
            raise Exception("Unable to measure feedback temperature")
        self.feedback_temp = feedback_temp

    def _try_get_target_temperature(self):
        target_temp = self.targetTemperatureService.try_get_target_temp()
        if not target_temp:
            raise Exception("Unable to set target temperature")
        self.target_temp = target_temp

    def _try_get_ambient_temperature(self):
        ambient_temp = self.ambientTemperatureService.try_get_ambient_temperature()
        if not ambient_temp:
            raise Exception("Unable to get ambient temperature")
        self.ambientTemp = ambient_temp

    def _try_control_temperature(self):
        boiler_active = self.temperatureControlService.try_compute_boiler_activation_signal(self.target_temp,
                                                                                            self.feedback_temp)
        if boiler_active is None:
            raise Exception("Unable to compute boiler actuation signal")

        if boiler_active is not self.boiler_active:
            self._try_set_boiler(boiler_active)

    def _try_set_boiler(self, boiler_active):
        is_success = self.boilerActuationService.try_actuate_boiler(boiler_active)
        if is_success is None:
            raise Exception("Unable to actuate boiler")

        self.boiler_active = boiler_active
