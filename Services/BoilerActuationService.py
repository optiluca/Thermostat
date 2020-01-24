import gpiozero

RELAY_PIN = 18

class BoilerActuationService:
    def __init__(self):
        self.relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

    def try_actuate_boiler(self, boilerActive):
        try:
            if boilerActive:
                self.relay.on()
            else:
                self.relay.off()
            return True
        except Exception as e:
            print(e)
            return False

