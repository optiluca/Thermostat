import gpiozero

RELAY_PIN = 18


class BoilerActuationService:
    def __init__(self):
        self.relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

    def try_actuate_boiler(self, boilerActive):
        self.set_boiler(boilerActive)
        return (False)

    def set_boiler(self, boilerActive):
        if boilerActive:
            print('Turning on boiler...')
            self.relay.on()
        else:
            print('Turning off boiler...')
            self.relay.off()
