import logging
from logging.handlers import RotatingFileHandler
from utils.main_utils import get_dir_size
from constants import LOGS_DIR
import time
import os


 

os.makedirs(LOGS_DIR, exist_ok=True)

# Better filename (readable timestamp)
FILE_NAME = os.path.join(LOGS_DIR, f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.log")

def config_logger():
    logger=logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler=RotatingFileHandler(
        FILE_NAME,
        maxBytes=2 * 1024 * 1024, # 2mb
        backupCount=5
    )

    formatter=logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    file_handler.setFormatter(formatter)

    console_handler=logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
  


config_logger()