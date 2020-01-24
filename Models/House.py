import numpy as np


class House:
    def __init__(self, K1, K2):
        self.K1 = K1
        self.K2 = K2

    def equilibrium_temperature(self, ambient_temperature, radiator_temperature, boiler_active):
        if boiler_active:
            temperature = (self.K1 * ambient_temperature + self.K2 * radiator_temperature) / (self.K1 + self.K2)
        else:
            temperature = ambient_temperature

        return temperature

    def temperature_at_time(self, initial_temperature, ambient_temperature, radiator_temperature, boiler_active,
                            initial_time, target_time):
        if boiler_active:
            decay_rate = self.K1 + self.K2
        else:
            decay_rate = self.K1

        equilibrium_temperature = self.equilibrium_temperature(ambient_temperature, radiator_temperature, boiler_active)
        time_elapsed = target_time - initial_time

        temperature = equilibrium_temperature + \
                      (initial_temperature - equilibrium_temperature) * np.exp(-1 * decay_rate * time_elapsed)
        return temperature
