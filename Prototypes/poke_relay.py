import gpiozero
import time

RELAY_PIN = 25


relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

while True:
    relay.on()
    time.sleep(0.2)
    relay.off()
    time.sleep(5)
