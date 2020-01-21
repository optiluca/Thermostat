import glob
import time

import gpiozero
import yaml

RELAY_PIN = 18

relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def set_boiler(status):
    if status:
        print('Turning on boiler...')
        relay.on()
    else:
        print('Turning off boiler...')
        relay.off()


def toggle_boiler():
    print('Toggling relay...')
    relay.toggle()


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


def read_config(file_path):
    with open(file_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config
