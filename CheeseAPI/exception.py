import sys, traceback, threading

from CheeseLog import logger

def sysExceptionHandle(*args):
    try:
        raise args[1]
    except:
        logger.error(f'''
{logger.encode(traceback.format_exc()[:-1])}''')

sys.excepthook = sysExceptionHandle

def threadException(*args, **kwargs):
    try:
        raise args[0][1]
    except:
        logger.danger(f'''
{logger.encode(traceback.format_exc()[:-1])}''')

threading.excepthook = threadException
