import time
from time import strftime


def current_timestamp():
    return int(round(time.time() * 1000))


def date_time(format='%d-%m-%Y_%H_%M_%S'):
    return strftime(format, time.localtime())
