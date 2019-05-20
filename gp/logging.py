## this module is not in use


import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from scrapy.utils.project import get_project_settings
import datetime

# print settings.get('NAME')

class scrapyLog:
    
    def __init__(self, loggerName):

        # settings=get_project_settings()
        # log_file = settings.get('LOG_FILE')
        # format_setting = settings.get('LOG_FORMAT')

        log_file = 'D:/Local/MMA/log_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt'
        format_setting = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

        self.mainLogger = logging.getLogger(loggerName)

        formatter = logging.Formatter(format_setting, "%Y-%m-%d %H:%M:%S")

        file_handler = TimedRotatingFileHandler(log_file, when = 'H', interval = 3)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        self.mainLogger.addHandler(file_handler)
    
    def getLogger(self):
        return self.mainLogger