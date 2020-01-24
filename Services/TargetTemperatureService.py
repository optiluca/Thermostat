import datetime
from utils import to_time


class TargetTemperatureService:
    def __init__(self, config):

        self.night_temp = config['temperatures']['night_temp']
        self.day_temp = config['temperatures']['day_temp']
        self.away_temp = config['temperatures']['away_temp']

        self.morning_beginning = to_time(config['times']['morning_beginning'])
        self.morning_end = to_time(config['times']['morning_end'])
        self.evening_beginning = to_time(config['times']['evening_beginning'])
        self.evening_end = to_time(config['times']['evening_end'])

    def try_get_target_temp(self):
        now = datetime.datetime.now()

        weekday = now.isoweekday()
        timeOfDay = now.time()

        isWeekend = weekday >= 6

        if timeOfDay < self.morning_beginning:
            targetTemp = self.night_temp
        elif timeOfDay < self.morning_end:
            targetTemp = self.day_temp
        elif timeOfDay < self.evening_beginning:
            if isWeekend:
                targetTemp = self.day_temp
            else:
                targetTemp = self.away_temp
        elif timeOfDay < self.evening_end:
            targetTemp = self.day_temp
        else:
            targetTemp = self.night_temp

        return targetTemp
