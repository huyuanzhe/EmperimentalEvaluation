import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler

log_file = 'FPsScore.log'


class LogAdapter(object):
    def __init__(self):
        pass

    def set_log(self, log_name):
        logger = logging.getLogger("{}".format(log_name))
        logger.setLevel(level=logging.DEBUG)
        log_handler = ConcurrentRotatingFileHandler('{}'.format(log_file), 'a', maxBytes=0, backupCount=10)
        log_handler.setLevel(logging.DEBUG)
        log_format = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(process)d %(levelname)s %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')
        log_handler.setFormatter(log_format)
        logger.addHandler(log_handler)

        return logger