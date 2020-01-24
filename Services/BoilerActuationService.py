import gpiozero

RELAY_PIN = 18

class BoilerActuationService:
    def __init__(self):
        self.relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

    def actuate_boiler(self, boilerActive):
        if boilerActive:
            self.relay.on()
        else:
            self.relay.off()

