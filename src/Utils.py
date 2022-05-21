import configparser
import time
import os
import logging

log = logging.getLogger('Utils')

weekday = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

num_to_weekday = {
     0: "Monday",
     1: "Tuesday",
     2: "Wednesday",
     3: "Thursday",
     4: "Friday",
     5: "Saturday",
     6: "Sunday"
}


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def get_config():
        config = configparser.ConfigParser()
        config.read('src/config.ini')
        log.info('Reading config.ini')
        return config

    @staticmethod
    def get_epoch():
        epoch_time = str(int(time.time()) * 1000)
        log.info('Calculating epoch time in milliseconds: {0}'.format(epoch_time))
        return epoch_time

    @staticmethod
    def does_file_exists(file_name, current_dir=True, dir=''):
        if current_dir:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(dir_path, file_name)
        else:
            path = os.path.join(dir, file_name)
        exists = os.path.exists(path)
        log.info('Checking if file {0} exists; Does it exist: {1}'.format(path, exists))
        return exists

