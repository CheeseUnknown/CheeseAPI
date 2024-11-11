import multiprocessing, queue
from typing import TYPE_CHECKING, Callable, Dict, overload, Any, Tuple, Literal
from datetime import datetime, timedelta
from asyncio import sleep as asyncio_sleep
from uuid import uuid4

from dill import loads, dumps

if TYPE_CHECKING:
    from CheeseAPI.app import App

datetime_now = datetime.now

class ScheduleTask:
    def __init__(self, app: 'App', key: str):
        self._app: 'App' = app
        self._key: str = key

    def reset(self):
        '''
        重置统计数据，例如`self.total_repetition_num`
        '''

        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'total_repetition_num': 0
        }

    @property
    def key(self) -> str:
        '''
        【只读】
        '''

        return self._key

    @property
    def timer(self) -> timedelta | Literal['PER_FRAME']:
        '''
        任务触发的间隔时间
        '''

        return self._app._managers_['schedules'][self.key]['timer']

    @timer.setter
    def timer(self, value: timedelta | Literal['PER_FRAME']):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'timer': value
        }

    @property
    def fn(self) -> Callable:
        return loads(self._app._managers_['schedules'][self.key]['fn'])

    @fn.setter
    def fn(self, value: Callable):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'fn': dumps(value, recurse = True),
            'needUpdate': True
        }

    @property
    def startTimer(self) -> datetime:
        '''
        自定义的开始时间。若未设置，则为当前时间
        '''

        return self._app._managers_['schedules'][self.key]['startTimer']

    @startTimer.setter
    def startTimer(self, value: datetime):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'startTimer': value
        }

        if self.auto_remove and self.expired:
            del self._app._managers_['schedules'][self.key]

    @property
    def auto_remove(self) -> bool:
        '''
        任务过期后是否自动删除

        若设置后`(self.expired or self.remaining_repetition_num == 0) and self.auto_remove`，则该任务会被立刻删除
        '''

        return self._app._managers_['schedules'][self.key]['auto_remove']

    @auto_remove.setter
    def auto_remove(self, value: bool):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'auto_remove': value
        }

        if self.auto_remove and (self.expired or self.remaining_repetition_num == 0):
            del self._app._managers_['schedules'][self.key]

    @property
    def active(self) -> bool:
        '''
        是否激活；未激活将忽略触发信号
        '''

        return self._app._managers_['schedules'][self.key]['active']

    @active.setter
    def active(self, value: bool):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'active': value
        }

    @property
    def inactive(self) -> bool:
        '''
        【只读】 是否未激活
        '''

        return not self._app._managers_['schedules'][self.key]['active']

    @property
    def expected_repetition_num(self) -> int | None:
        '''
        期望的重复次数

        若设置后`self.remaining_repetition_num == 0 and self.auto_remove`，则该任务会被立刻删除
        '''

        return self._app._managers_['schedules'][self.key]['expected_repetition_num']

    @expected_repetition_num.setter
    def expected_repetition_num(self, value: int | None):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'expected_repetition_num': value
        }

    @property
    def total_repetition_num(self) -> int:
        '''
        【只读】 总计的重复次数
        '''

        return self._app._managers_['schedules'][self.key]['total_repetition_num']

    @property
    def remaining_repetition_num(self) -> int | None:
        '''
        【只读】 剩余的重复次数
        '''

        if self.expected_repetition_num is None:
            return
        return self.expected_repetition_num - self.total_repetition_num

    @property
    def unexpired(self) -> bool | None:
        '''
        【只读】 任务是否未过期
        '''

        if self.endTimer:
            return self.endTimer > datetime_now()

    @property
    def expired(self) -> bool | None:
        '''
        【只读】 任务是否过期
        '''

        if self.unexpired is None:
            return
        return not self.unexpired

    @property
    def lastTimer(self) -> datetime | None:
        '''
        【只读】 任务上一次的触发时间；`None`代表从未触发过
        '''

        return self._app._managers_['schedules'][self.key]['lastTimer']

    @property
    def intervalTime(self) -> float:
        '''
        最小检查间隔
        '''

        return self._app._managers_['schedules'][self.key]['intervalTime']

    @intervalTime.setter
    def intervalTime(self, value: float):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'intervalTime': value
        }

    @property
    def lastReturn(self) -> Any:
        '''
        【只读】 上一次的返回值
        '''

        return loads(self._app._managers_['schedules'][self.key]['lastReturn'])

    @property
    def endTimer(self) -> datetime | None:
        '''
        自定义的结束时间。若未设置，则为当前时间

        若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除
        '''

        return self._app._managers_['schedules'][self.key]['endTimer']

    @endTimer.setter
    def endTimer(self, value: datetime | None):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'endTimer': value
        }

        if self.auto_remove and self.expired:
            del self._app._managers_['schedules'][self.key]

class Scheduler:
    def __init__(self, app: 'App'):
        self._app: 'App' = app
        self._taskHandlers: Dict[str, multiprocessing.Process] = {}
        self._queues: Dict[str, Tuple[queue.Queue, queue.Queue]] = {}

    async def _taskHandle(self, key: str):
        task = self.tasks[key]
        queues = self._queues[key]

        if task.timer == 'PER_FRAME':
            queues[1].put(None)
            while True:
                if not queues[0].empty():
                    if queues[0].get_nowait():
                        await self._afterHandle(key)
                        break
                    else:
                        await self._beforeHandle(key)
                        queues[1].put(None)
                await asyncio_sleep(0)
        else:
            if not queues[0].empty():
                if queues[0].get_nowait():
                    await self._afterHandle(key)
                else:
                    await self._beforeHandle(key)
                    queues[1].put(None)

    def _processHandle(self, key: str, queues: Tuple[queue.Queue, queue.Queue]):
        from gc import disable, enable
        from time import time, sleep

        import setproctitle
        from CheeseLog import logger
        from dill import dumps

        logger_debug = logger.debug
        logger_encode = logger.encode
        datetime_fromtimestamp = datetime.fromtimestamp

        setproctitle.setproctitle(f'{setproctitle.getproctitle()}:SchedulerTask:{key}')

        task: ScheduleTask = self._app.scheduler.tasks[key]
        fn = task.fn
        intervalTime = task.intervalTime
        taskTime = self._app.server.intervalTime if task.timer == 'PER_FRAME' else task.timer.total_seconds()
        lastTime = lastRunTime = triggeredTime = time()

        while True:
            task: ScheduleTask = self._app.scheduler.tasks.get(key)
            if not task or task.expired or task.remaining_repetition_num == 0 or task.inactive:
                break

            _time = time()

            triggeredTime = lastRunTime + taskTime
            if (task.timer == 'PER_FRAME' or triggeredTime - intervalTime / 2 < _time) and task.active:
                if task.timer == 'PER_FRAME':
                    queues[1].get()
                    _time = time()
                queues[0].put(False)
                queues[1].get()
                disable()
                runTime = time()

                if self._app._managers_['schedules'][task.key]['needUpdate']:
                    fn = task.fn
                    self._app._managers_['schedules'][task.key] = {
                        **self._app._managers_['schedules'][task.key],
                        'needUpdate': False
                    }

                result = fn(task.lastReturn, **{
                    'intervalTime': runTime - lastRunTime
                })

                self._app._managers_['schedules'][task.key] = {
                    **self._app._managers_['schedules'][task.key],
                    'total_repetition_num': task.total_repetition_num + 1,
                    'lastTimer': datetime_fromtimestamp(runTime),
                    'lastReturn': dumps(result, recurse = True)
                }
                queues[0].put(True)

                _runTime = time() - (_time if task.timer == 'PER_FRAME' else runTime)
                if _runTime > taskTime:
                    logger_debug(f'SchedulerTask: {logger_encode(task.key)}\nActual run time greater than expected run time. Recommendations for shorter task run time or longer running cycles\n  Expected run time: {taskTime:.6f}s\n  Actual run time:   {_runTime:.6f}s', f'SchedulerTask: {logger_encode(task.key)}\nActual run time greater than expected run time. Recommendations for shorter task run time or longer running cycles\n  Expected run time: <blue>{taskTime:.6f}</blue> seconds\n  Actual run time:   <blue>{_runTime:.6f}</blue> seconds')

                lastRunTime = runTime
                enable()

            sleep(max(intervalTime - _time + lastTime, 0))
            lastTime = _time

    async def _beforeHandle(self, key: str):
        task = self._app.scheduler.get_task(key)
        await self._app._handle.scheduler_beforeRunning(task)
        await self._app.signal.scheduler_beforeRunning.async_send(**{
            'task': task
        })

    async def _afterHandle(self, key: str):
        task = self._app.scheduler.get_task(key)
        await self._app.signal.scheduler_afterRunning.async_send(**{
            'task': task
        })
        await self._app._handle.scheduler_afterRunning(task)

    @overload
    def add(self, fn: Callable, *, timer: timedelta | Literal['PER_FRAME'] | None = None, key: str | None = None, startTimer: datetime | None = None, expected_repetition_num: int | None = None, auto_remove: bool = False, intervalTime: float | None = None, endTimer: datetime | None = None):
        '''
        通过函数添加一个任务；若需要获取任务或删除任务，请为其设置一个key

        >>> import datetime
        >>>
        >>> from CheeseAPI import app
        >>>
        >>> def task(lastReturn, *, intervalTime: float, **_):
        ...    print('Hello World.')
        ...
        >>> app.scheduler.add(datetime.timedelta(days = 1), task)

        - Args
            - timer: 触发任务的间隔时间，"PER_FRAME"代表该任务会在每一帧运行

            - startTimer: 为该计划设定一个开始时间，而不是使用当前时间

            - expected_repetition_num: 期望的重复次数

            - auto_remove: 若当前计划过期或执行次数达到预期次数，是否自动删除该计划

            - intervalTime: 最小检查间隔；默认为`app.server.intervalTime`

            - endTimer: 为该计划设定一个结束时间
        '''

    @overload
    def add(self, *, timer: timedelta | Literal['PER_FRAME'] | None = None, key: str | None = None, startTimer: datetime | None = None, expected_repetition_num: int | None = None, auto_remove: bool = False, intervalTime: float | None = None, endTimer: datetime | None = None):
        '''
        通过装饰器添加一个任务；若需要获取任务或删除任务，请为其设置一个key

        >>> import datetime
        >>>
        >>> from CheeseAPI import app
        >>>
        >>> @app.scheduler.add(timer = datetime.timedelta(days = 1))
        >>> def task(lastReturn, *, intervalTime: float, **_):
        ...    print('Hello World.')

        - Args
            - timer: 触发任务的间隔时间，"PER_FRAME"代表该任务会在每一帧运行

            - startTimer: 为该计划设定一个开始时间，而不是使用当前时间

            - expected_repetition_num: 期望的重复次数

            - auto_remove: 若当前计划过期或执行次数达到预期次数，是否自动删除该计划

            - intervalTime: 最小检查间隔；默认为`app.server.intervalTime`

            - endTimer: 为该计划设定一个结束时间
        '''

    def add(self, fn: Callable | None = None, *, timer: timedelta | Literal['PER_FRAME'] | None = None, key: str | None = None, startTimer: datetime | None = None, expected_repetition_num: int | None = None, auto_remove: bool = False, intervalTime: float | None = None, endTimer: datetime | None = None):
        if timer is None:
            timer = timedelta(seconds = intervalTime or self._app.server.intervalTime)

        if key is None:
            key = str(uuid4())

        if startTimer is None:
            startTimer = datetime_now()

        if fn:
            self._app._managers_['schedules'][key] = {
                'timer': timer,
                'fn': dumps(fn, recurse = True),
                'startTimer': startTimer,
                'expected_repetition_num': expected_repetition_num,
                'total_repetition_num': 0,
                'auto_remove': auto_remove,
                'active': True,
                'lastTimer': None,
                'intervalTime': intervalTime or (self._app.server.intervalTime if timer == 'PER_FRAME' else timer.total_seconds()) / 10,
                'lastReturn': dumps(None, recurse = True),
                'needUpdate': False,
                'endTimer': endTimer
            }
            return

        def wrapper(fn):
            self._app._managers_['schedules'][key] = {
                'timer': timer,
                'fn': dumps(fn, recurse = True),
                'startTimer': startTimer,
                'expected_repetition_num': expected_repetition_num,
                'total_repetition_num': 0,
                'auto_remove': auto_remove,
                'active': True,
                'lastTimer': None,
                'intervalTime': intervalTime or (self._app.server.intervalTime if timer == 'PER_FRAME' else timer.total_seconds()) / 10,
                'lastReturn': dumps(None, recurse = True),
                'needUpdate': False,
                'endTimer': endTimer
            }
            return fn
        return wrapper

    def remove(self, key: str):
        '''
        删除计划

        >>> import datetime
        >>>
        >>> from CheeseAPI import app
        >>>
        >>> @app.scheduler.add(timer = datetime.timedelta(days = 1), key = 'myTask')
        >>> def task(lastReturn, *, intervalTime: float, **_):
        ...    print('Hello World.')
        ...
        >>> app.scheduler.remove('myTask')
        '''

        if key in self._app._managers_['schedules']:
            del self._app._managers_['schedules'][key]

    def get_task(self, key: str) -> ScheduleTask | None:
        '''
        获取`ScheduleTask`，`ScheduleTask`请查看[Schedule](../Schedule.md)

        >>> import datetime
        >>>
        >>> from CheeseAPI import app
        >>>
        >>> @app.scheduler.add(timer = datetime.timedelta(days = 1), key = 'myTask')
        >>> def task(lastReturn, *, intervalTime: float, **_):
        ...     print('Hello World.')
        ...
        >>> myTask = app.scheduler.get_task('myTask')
        '''

        if key in self._app._managers_['schedules']:
            return ScheduleTask(self._app, key)

    @property
    def tasks(self) -> Dict[str, ScheduleTask]:
        '''
        【只读】 所有的任务

        未指定key的任务会自动分配一个uuid字符串为key
        '''

        return {
            key: ScheduleTask(self._app, key) for key in self._app._managers_['schedules'].keys()
        }
