import sys, traceback, threading

from CheeseLog import error, danger

def sysException(*args, **kwargs):
    try:
        raise args[1]
    except:
        error(f'The error occured while the program running:\n{traceback.format_exc()}'[:-1])
sys.excepthook = sysException

def threadException(*args, **kwargs):
    try:
        raise args[0][1]
    except:
        danger(f'The error occured while the program running:\n{traceback.format_exc()}'[:-1])
threading.excepthook = threadException
