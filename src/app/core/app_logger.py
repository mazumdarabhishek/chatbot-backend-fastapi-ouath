import logging
from logging.handlers import TimedRotatingFileHandler
from app.core.config import settings
import os
import sys
import colorlog



def setup_daily_logger(logger_name, log_directory = settings.logs_directory):
    
    os.makedirs(log_directory, exist_ok=True)
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(settings.log_level)
    
    log_file = os.path.join(log_directory, 'app.log')
    file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(name)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    for name in logging.root.manager.loggerDict:
        if name in ("uvicorn"):
            uvicorn_logger = logging.getLogger(name)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.addHandler(file_handler)
            uvicorn_logger.addHandler(console_handler)
            uvicorn_logger.setLevel(settings.log_level)
    
    return logger
