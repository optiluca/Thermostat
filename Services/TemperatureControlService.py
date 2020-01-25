class TemperatureControlService:
    def __init__(self):
        self.hysteresis = 0.5

    def try_compute_boiler_control_signal(self, target_temp, feedback_temp):
        control_signal = 0

        if feedback_temp > target_temp + self.hysteresis:
            control_signal = -1
        elif feedback_temp < target_temp - self.hysteresis:
            control_signal = 1

        return control_signal
