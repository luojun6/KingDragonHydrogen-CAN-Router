#!/usr/bin/pthon

import os
import logging

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_logger(logger_name="logger", logging_level=logging.DEBUG):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    channel = logging.StreamHandler()
    channel.setLevel(logging_level)

    formatter = logging.Formatter(
        f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    channel.setFormatter(formatter)
    logger.addHandler(channel)
    
    return logger

class CanException(Exception):
    pass