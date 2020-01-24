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
        time_of_day = now.time()

        is_weekend = weekday >= 6

        if time_of_day < self.morning_beginning:
            target_temp = self.night_temp
        elif time_of_day < self.morning_end:
            target_temp = self.day_temp
        elif time_of_day < self.evening_beginning:
            if is_weekend:
                target_temp = self.day_temp
            else:
                target_temp = self.away_temp
        elif time_of_day < self.evening_end:
            target_temp = self.day_temp
        else:
            target_temp = self.night_temp

        return target_temp
