import sys, threading
from traceback import format_exc

from CheeseLog import logger

logger_error = logger.error
logger_encode = logger.encode
logger_danger = logger.danger

class Route_404_Exception(BaseException):
    ...

class Route_405_Exception(BaseException):
    ...

def sysExceptionHandle(*args):
    try:
        raise args[1]
    except:
        logger_error(f'''
{logger_encode(format_exc()[:-1])}''')

sys.excepthook = sysExceptionHandle

def threadException(*args, **kwargs):
    try:
        raise args[0][1]
    except:
        logger_danger(f'''
{logger_encode(format_exc()[:-1])}''')

threading.excepthook = threadException
