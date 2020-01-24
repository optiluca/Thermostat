import pyowm


class AmbientTemperatureService:
    def __init__(self, config):
        # OWM
        self.owm = pyowm.OWM(config['tokens']['openweathermap'], subscription_type='free')
        self.lat = config['coordinates']['latitude']
        self.lon = config['coordinates']['longitude']
        pass

    def try_get_ambient_temperature(self):
        ambientTemp = None

        try:
            ambientTemp = self.owm.weather_at_coords(self.lat, self.lon).get_weather().get_temperature(unit='celsius')
            ['temp']
        except Exception as e:
            print(e)

        return ambientTemp
