import numpy as np


class House:
    def __init__(self, k1, k2):
        self.k1 = k1
        self.k2 = k2

    def equilibrium_temperature(self, ambient_temperature, radiator_temperature, boiler_active):
        if boiler_active:
            temperature = (self.k1 * ambient_temperature + self.k2 * radiator_temperature) / (self.k1 + self.k2)
        else:
            temperature = ambient_temperature

        return temperature

    def temperature_at_time(self, initial_temperature, ambient_temperature, radiator_temperature, boiler_active,
                            initial_time, target_time):
        if boiler_active:
            decay_rate = self.k1 + self.k2
        else:
            decay_rate = self.k1

        equilibrium_temperature = self.equilibrium_temperature(ambient_temperature, radiator_temperature, boiler_active)
        time_elapsed = target_time - initial_time

        temperature = equilibrium_temperature + \
                      (initial_temperature - equilibrium_temperature) * np.exp(-1 * decay_rate * time_elapsed)
        return temperature
