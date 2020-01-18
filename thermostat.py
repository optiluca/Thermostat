import datetime
import sys
import time

from utils import set_boiler, read_temp

NIGHT_TEMP = 15
DAY_TEMP = 18
AWAY_TEMP = 13

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

        print('Target T: {}, Current T: {}'.format(t_target, t_current))

        if t_current > t_target + HYST:
            set_boiler(False)
        elif t_current < t_target - HYST:
            set_boiler(True)
        time.sleep(30)


if __name__ == "__main__":
    print('Starting...')
    try:
        main_loop()
    except KeyboardInterrupt:
        # turn the relay off
        set_boiler(False)
        print("\nExiting application\n")
        time.sleep(3)
        # exit the application
        sys.exit(0)
