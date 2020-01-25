import datetime
import yaml
import logging
import numpy as np
from logging.handlers import TimedRotatingFileHandler


def read_config(file_path):
    config = None
    with open(file_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def select_when_flag_true(x, flag):
    indices = np.nonzero(flag[1:] != flag[:-1])[0] + 1
    xs = np.split(x, indices)
    xs = xs[0::2] if flag[0] else xs[1::2]
    return xs


def to_time(t):
    if isinstance(t, int) or isinstance(t, float):
        t = str(int(t)).zfill(4)
    return datetime.datetime.strptime(t, '%H%M').time()


def setup_logger(log_file, level=logging.INFO):
    # Configure log file
    logger = logging.getLogger()
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, delay=False)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
