import sys, traceback, threading

from CheeseLog import logger

def sysExceptionHandle(*args, **kwargs):
    try:
        raise args[1]
    except:
        logger.error(f'''The server exited with an error:
{logger.encode(traceback.format_exc()[:-1])}''')

sys.excepthook = sysExceptionHandle

def threadException(*args, **kwargs):
    try:
        raise args[0][1]
    except:
        logger.danger(f'''The error occured in the {threading.currentThread().getName()}:
{logger.encode(traceback.format_exc()[:-1])}''')

threading.excepthook = threadException
