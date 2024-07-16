'''
1分钟检测一次，当时间位于0点时，自动删除第90天前的日志。
'''

import datetime, os

from CheeseAPI import app
from CheeseLog import logger

EXPIRED_DAY = 90

app.workspace.logger = True

now = datetime.datetime.now()
startTimer = datetime.datetime(now.year, now.month, now.day)

@app.scheduler.add(timer = datetime.timedelta(days = 1), startTimer = startTimer, key = 'Logger:Expirer', intervalTime = 60)
def loggerExpirer(*args, **kwargs):
    from CheeseAPI import app

    date = datetime.datetime.now() - datetime.timedelta(days = EXPIRED_DAY)
    loggerFile = date.strftime(os.path.join(app.workspace.base, app.workspace.log, app.workspace.logger))
    if os.path.exists(loggerFile):
        os.remove(loggerFile)
        logger.default('INFO', f'Deleted expired log {os.path.relpath(loggerFile, app.workspace.base)}', f'Deleted expired log <cyan>{os.path.relpath(loggerFile, app.workspace.base)}</cyan>')

app.run()
