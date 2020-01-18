import time

from utils import read_temp

while True:
    print(read_temp())
    time.sleep(1)
