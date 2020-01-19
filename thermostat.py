import datetime
import logging
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from logging import FileHandler

from utils import set_boiler, read_temp

NIGHT_TEMP = 15
DAY_TEMP = 15
AWAY_TEMP = 15

HYST = 1


def get_target_temp():
    morning_beginning = datetime.time(hour=7)
    morning_end = datetime.time(hour=8, minute=30)

    evening_beginning = datetime.time(hour=18)
    evening_end = datetime.time(hour=23)

    now = datetime.datetime.now()

    weekday = now.isoweekday()
    timeofday = now.time()

    is_weekend = weekday >= 6

    if timeofday < morning_beginning:
        temp = NIGHT_TEMP
    elif timeofday < morning_end:
        temp = DAY_TEMP
    elif timeofday < evening_beginning:
        if is_weekend:
            temp = DAY_TEMP
        else:
            temp = AWAY_TEMP
    elif timeofday < evening_end:
        temp = DAY_TEMP
    else:
        temp = NIGHT_TEMP

    return temp


def main_loop():
    while True:
        t_current = read_temp()
        t_target = get_target_temp()

        status_string = 'Target T: {}, Current T: {}'.format(t_target, t_current)
        print(status_string)
        logging.info(status_string)

        if t_current > t_target + HYST:
            boiler_state = False
        elif t_current < t_target - HYST:
            boiler_state = True
        else:
            boiler_state = None

        if boiler_state is not None:
            set_boiler(boiler_state)
            logging.info('Boiler state: {}'.format(boiler_state))

        time.sleep(30)


def setup_logger(logger_name='SimpleThermostatLogger', log_file='Thermostat.log', level=logging.INFO):
    # Configure log file
    l = logging.getLogger(logger_name)
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)
    # file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, delay=False)
    file_handler = FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)


if __name__ == "__main__":
    print('Starting...')

    setup_logger()

    try:
        main_loop()
    except KeyboardInterrupt:
        set_boiler(False)
        sys.exit(0)
