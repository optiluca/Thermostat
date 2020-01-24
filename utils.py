import datetime
import yaml

def try_read_config(file_path):
    isSuccess = False
    config = None
    with open(file_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            isSuccess = True
        except yaml.YAMLError as exc:
            print(exc)
    return (isSuccess, config)

def to_time(t):
    if isinstance(t, int) or isinstance(t, float):
        t = str(int(t)).zfill(4)
    return datetime.datetime.strptime(t, '%H%M').time()