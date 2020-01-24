import sys
import time

from utils import set_boiler, read_temp


def main_loop():
    set_boiler(False)
    while True:
        set_boiler(True)
        time.sleep(5)
        set_boiler(False)
        print(read_temp())
        time.sleep(5)


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
