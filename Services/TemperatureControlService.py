class TemperatureControlService:
    def __init__(self):
        self.hysteresis = 0.5

    def try_compute_boiler_activation_signal(self, targetTemp, feedbackTemp):
        activateBoiler = None

        if feedbackTemp > targetTemp + self.hysteresis:
            activateBoiler = False
        elif feedbackTemp < targetTemp - self.hysteresis:
            activateBoiler = True

        return activateBoiler
