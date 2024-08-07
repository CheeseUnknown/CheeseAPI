import uuid, datetime, multiprocessing, threading, time, queue
from typing import TYPE_CHECKING, Callable, Dict, overload, Any

import dill, setproctitle

if TYPE_CHECKING:
    from CheeseAPI.app import App

class ScheduleTask:
    def __init__(self, app: 'App', key: str):
        self._app: 'App' = app
        self._key: str = key

    def reset(self):
        '''
        重置统计数据，例如`self.total_repetition_num`。
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
    def timer(self) -> datetime.timedelta:
        '''
        任务触发的间隔时间。
        '''

        return self._app._managers_['schedules'][self.key]['timer']

    @timer.setter
    def timer(self, value: datetime.timedelta):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'timer': value
        }

    @property
    def fn(self) -> Callable:
        return dill.loads(self._app._managers_['schedules'][self.key]['fn'])

    @fn.setter
    def fn(self, value: Callable):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'fn': dill.dumps(value, recurse = True),
            'needUpdate': True
        }

    @property
    def startTimer(self) -> datetime.datetime:
        '''
        自定义的开始时间。若未设置，则为当前时间。

        若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。
        '''

        return self._app._managers_['schedules'][self.key]['startTimer']

    @startTimer.setter
    def startTimer(self, value: datetime.datetime):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'startTimer': value
        }

        if self.auto_remove and self.expired:
            del self._app._managers_['schedules'][self.key]

    @property
    def auto_remove(self) -> bool:
        '''
        任务过期后是否自动删除。

        若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。
        '''

        return self._app._managers_['schedules'][self.key]['auto_remove']

    @auto_remove.setter
    def auto_remove(self, value: bool):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'auto_remove': value
        }

        if self.auto_remove and self.expired:
            del self._app._managers_['schedules'][self.key]

    @property
    def active(self) -> bool:
        '''
        是否激活；未激活将忽略触发信号。
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
        【只读】 是否未激活。
        '''

        return not self._app._managers_['schedules'][self.key]['active']

    @property
    def expected_repetition_num(self) -> int:
        '''
        期望的重复次数；0代表无限次数。

        若设置后`self.expired and self.auto_remove`，则该任务会被立刻删除。
        '''

        return self._app._managers_['schedules'][self.key]['expected_repetition_num']

    @expected_repetition_num.setter
    def expected_repetition_num(self, value: int):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'expected_repetition_num': value
        }

    @property
    def total_repetition_num(self) -> int:
        '''
        【只读】 总计的重复次数。
        '''

        return self._app._managers_['schedules'][self.key]['total_repetition_num']

    @property
    def remaining_repetition_num(self) -> int:
        '''
        【只读】 剩余的重复次数；-1代表无限次重复。
        '''

        if self.expected_repetition_num == 0:
            return -1
        return self.expected_repetition_num - self.total_repetition_num

    @property
    def unexpired(self) -> bool:
        '''
        【只读】 任务是否未过期。
        '''

        if self.expected_repetition_num == 0:
            return True

        return self.startTimer + self.timer * (self.expected_repetition_num + 1) >= datetime.datetime.now()

    @property
    def expired(self) -> bool:
        '''
        【只读】 任务是否过期。
        '''

        return not self.unexpired

    @property
    def lastTimer(self) -> datetime.datetime | None:
        '''
        【只读】 任务上一次的触发时间；`None`代表从未触发过。
        '''

        return self._app._managers_['schedules'][self.key]['lastTimer']

    @property
    def intervalTime(self) -> float:
        '''
        最小检查间隔。
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
        【只读】 上一次的返回值。
        '''

        return dill.loads(self._app._managers_['schedules'][self.key]['lastReturn'])

class Scheduler:
    def __init__(self, app: 'App'):
        self._app: 'App' = app
        self._taskHandlers: Dict[str, multiprocessing.Process | threading.Thread] = {}
        self._inputQueue: queue.Queue = multiprocessing.Queue()
        self._outputQueue: queue.Queue = multiprocessing.Queue()

    def _processHandle(self, key: str):
        setproctitle.setproctitle(f'{setproctitle.getproctitle()}:SchedulerTask:{key}')

        task: ScheduleTask = self._app.scheduler.tasks[key]
        lastTimer = datetime.datetime.now()
        fn = task.fn

        while True:
            task: ScheduleTask = self._app.scheduler.tasks.get(key)
            if not task or task.expired or task.inactive:
                break

            _timer = datetime.datetime.now()

            triggeredTimer = task.startTimer + task.timer * task.total_repetition_num
            if (lastTimer < triggeredTimer <= _timer or lastTimer > triggeredTimer + task.timer) and task.active:
                self._outputQueue.put(['before', task.key])

                self._inputQueue.get()

                if self._app._managers_['schedules'][task.key]['needUpdate']:
                    fn = task.fn
                    self._app._managers_['schedules'][task.key] = {
                        **self._app._managers_['schedules'][task.key],
                        'needUpdate': False
                    }

                result = fn(task.lastReturn, **{
                    'intervalTime': (_timer - lastTimer).total_seconds()
                })

                self._app._managers_['schedules'][task.key] = {
                    **self._app._managers_['schedules'][task.key],
                    'total_repetition_num': task.total_repetition_num + 1,
                    'lastTimer': _timer,
                    'lastReturn': dill.dumps(result, recurse = True)
                }

                self._outputQueue.put(['after', task.key])

            lastTimer = _timer
            time.sleep(max(task.intervalTime - (_timer - lastTimer).total_seconds(), 0))

    @overload
    def add(self, fn: Callable, *, timer: datetime.timedelta | None = None, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False, intervalTime: float | None = None):
        '''
        通过函数添加一个任务；若需要获取任务或删除任务，请为其设置一个key。

        ```python
        import datetime

        from CheeseAPI import app

        async def task(lastReturn, *, intervalTime: float, **_):
            print('Hello World.')

        app.scheduler.add(datetime.timedelta(days = 1), task)
        ```

        - Args

            - timer: 触发任务的间隔时间。

            - startTimer: 为该计划设定一个开始时间，而不是使用当前时间。

            - expected_repetition_num: 期望的重复次数，0代表无限重复。

            - auto_remove: 若`expected_repetition_num > 0`且当前计划过期，是否自动删除该计划。


            - intervalTime: 最小检查间隔；默认为`app.server.intervalTime`。
        '''

    @overload
    def add(self, *, timer: datetime.timedelta | None = None, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False, intervalTime: float | None = None):
        '''
        通过装饰器添加一个任务；若需要获取任务或删除任务，请为其设置一个key。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(timer = datetime.timedelta(days = 1))
        async def task(lastReturn, *, intervalTime: float, **_):
            print('Hello World.')
        ```

        - Args

            - timer: 触发任务的间隔时间。

            - startTimer: 为该计划设定一个开始时间，而不是使用当前时间。

            - expected_repetition_num: 期望的重复次数，0代表无限重复。

            - auto_remove: 若`expected_repetition_num > 0`且当前计划过期，是否自动删除该计划。

            - intervalTime: 最小检查间隔；默认为`app.server.intervalTime`。
        '''

    def add(self, fn: Callable | None = None, *, timer: datetime.timedelta | None = None, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False, intervalTime: float | None = None):
        if timer is None:
            timer = datetime.timedelta(seconds = intervalTime or self._app.server.intervalTime)

        if key is None:
            key = str(uuid.uuid4())

        if startTimer is None:
            startTimer = datetime.datetime.now()

        if fn:
            self._app._managers_['schedules'][key] = {
                'timer': timer,
                'fn': dill.dumps(fn, recurse = True),
                'startTimer': startTimer,
                'expected_repetition_num': expected_repetition_num,
                'total_repetition_num': 0,
                'auto_remove': auto_remove,
                'active': True,
                'lastTimer': None,
                'intervalTime': intervalTime or self._app.server.intervalTime,
                'lastReturn': dill.dumps(None, recurse = True),
                'needUpdate': False
            }
            return

        def wrapper(fn):
            self._app._managers_['schedules'][key] = {
                'timer': timer,
                'fn': dill.dumps(fn, recurse = True),
                'startTimer': startTimer,
                'expected_repetition_num': expected_repetition_num,
                'total_repetition_num': 0,
                'auto_remove': auto_remove,
                'active': True,
                'lastTimer': None,
                'intervalTime': intervalTime or self._app.server.intervalTime,
                'lastReturn': dill.dumps(None, recurse = True),
                'needUpdate': False
            }
            return fn
        return wrapper

    def remove(self, key: str):
        '''
        删除计划。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(timer = datetime.timedelta(days = 1), key = 'myTask')
        async def task(lastReturn, *, intervalTime: float, **_):
            print('Hello World.')

        app.scheduler.remove('myTask')
        ```
        '''

        if key in self._app._managers_['schedules']:
            del self._app._managers_['schedules'][key]

    def get_task(self, key: str) -> ScheduleTask:
        '''
        获取`ScheduleTask`，`ScheduleTask`请查看[Schedule](../Schedule.md)。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(timer = datetime.timedelta(days = 1), key = 'myTask')
        async def task(lastReturn, *, intervalTime: float, **_):
            print('Hello World.')

        myTask = app.scheduler.get_task('myTask')
        ```
        '''

        return ScheduleTask(self._app, key)

    @property
    def tasks(self) -> Dict[str, ScheduleTask]:
        '''
        【只读】 所有的任务。

        未指定key的任务会自动分配一个uuid字符串为key。
        '''

        return {
            key: ScheduleTask(self._app, key) for key in self._app._managers_['schedules'].keys()
        }
