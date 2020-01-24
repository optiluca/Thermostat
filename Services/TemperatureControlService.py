class TemperatureControlService:
    def __init__(self):
        self.hysteresis = 0.5

    def try_compute_boiler_activation_signal(self, target_temp, feedback_temp):
        activate_boiler = None

        if feedback_temp > target_temp + self.hysteresis:
            activate_boiler = False
        elif feedback_temp < target_temp - self.hysteresis:
            activate_boiler = True

        return activate_boiler
