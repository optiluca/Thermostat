import time
import glob


class TemperatureMeasurementService:
    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'
        pass

    def try_get_feedback_temperature(self):
        feedbackTemp = None

        lines = self.__read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.__read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            feedbackTemp = float(temp_string) / 1000.0

        return feedbackTemp

    def __read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
