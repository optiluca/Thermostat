import time
import glob

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

class FeedbackTemperatureAcquisitionService:
    def __init__(self, config):
        pass

    def try_get_feedback_temperature(self):
        feedbackTemp = None

        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            feedbackTemp = float(temp_string) / 1000.0

        return (False, feedbackTemp)

    def read_temp_raw(self):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines