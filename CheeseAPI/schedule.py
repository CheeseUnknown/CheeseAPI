import uuid, datetime
from typing import TYPE_CHECKING, Callable, Dict, overload

import dill

if TYPE_CHECKING:
    from CheeseAPI.app import App

class ScheduleTask:
    def __init__(self, app: 'App', key: str):
        self._app: 'App' = app
        self.key = key

    def reset(self):
        '''
        重置统计数据，例如`self.total_repetition_num`。
        '''

        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'total_repetition_num': 0
        }

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
            'fn': dill.dumps(value)
        }

    @property
    def startTimer(self) -> datetime.datetime:
        '''
        自定义的开始时间。若未设置，则为当前时间。

        若设置后`self.is_expired and self.auto_remove`，则该任务会被立刻删除。
        '''

        return self._app._managers_['schedules'][self.key]['startTimer']

    @startTimer.setter
    def startTimer(self, value: datetime.datetime):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'startTimer': value
        }

        if self.auto_remove and self.is_expired:
            del self._app._managers_['schedules'][self.key]

    @property
    def auto_remove(self) -> bool:
        '''
        任务过期后是否自动删除。

        若设置后`self.is_expired and self.auto_remove`，则该任务会被立刻删除。
        '''

        return self._app._managers_['schedules'][self.key]['auto_remove']

    @auto_remove.setter
    def auto_remove(self, value: bool):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'auto_remove': value
        }

        if self.auto_remove and self.is_expired:
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

        if self.auto_remove and self.is_expired:
            del self._app._managers_['schedules'][self.key]

    @property
    def expected_repetition_num(self) -> int:
        '''
        期望的重复次数；0代表无限次数。

        若设置后`self.is_expired and self.auto_remove`，则该任务会被立刻删除。
        '''

        return self._app._managers_['schedules'][self.key]['expected_repetition_num']

    @expected_repetition_num.setter
    def expected_repetition_num(self, value: int):
        self._app._managers_['schedules'][self.key] = {
            **self._app._managers_['schedules'][self.key],
            'expected_repetition_num': value
        }

        if self.auto_remove and self.is_expired:
            del self._app._managers_['schedules'][self.key]

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
    def is_unexpired(self) -> bool:
        '''
        【只读】 任务是否未过期。
        '''

        if self.expected_repetition_num == 0:
            return True

        return self.startTimer + self.timer * (self.expected_repetition_num + 1) >= datetime.datetime.now()

    @property
    def is_expired(self) -> bool:
        '''
        【只读】 任务是否过期。
        '''

        return not self.is_unexpired

class Scheduler:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

    @overload
    def add(self, timer: datetime.timedelta, fn: Callable, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False):
        '''
        通过函数添加一个任务。

        任务函数必须为协程函数。

        ```python
        import datetime

        from CheeseAPI import app

        async def task():
            print('Hello World.')

        app.scheduler.add(datetime.timedelta(days = 1), task)
        ```

        - Args

            - timer: 触发任务的间隔时间。

            - startTimer: 为该计划设定一个开始时间，而不是使用当前时间。

            - expected_repetition_num: 期望的重复次数，0代表无限重复。

            - auto_remove: 若`expected_repetition_num > 0`且当前计划过期，是否自动删除该计划。
        '''

    @overload
    def add(self, timer: datetime.timedelta, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False):
        '''
        通过装饰器添加一个任务。

        任务函数必须为协程函数。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(datetime.timedelta(days = 1))
        async def task():
            print('Hello World.')
        ```

        - Args

            - timer: 触发任务的间隔时间。

            - startTimer: 为该计划设定一个开始时间，而不是使用当前时间。

            - expected_repetition_num: 期望的重复次数，0代表无限重复。

            - auto_remove: 若`expected_repetition_num > 0`且当前计划过期，是否自动删除该计划。
        '''

    def add(self, timer: datetime.timedelta, fn: Callable | None = None, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False):
        if not key:
            key = str(uuid.uuid4())

        if not startTimer:
            startTimer = datetime.datetime.now()

        if fn:
            self._app._managers_['schedules'][key] = {
                'timer': timer,
                'fn': dill.dumps(fn),
                'startTimer': startTimer,
                'expected_repetition_num': expected_repetition_num,
                'total_repetition_num': 0,
                'auto_remove': auto_remove,
                'active': True
            }
            return

        def decorator(fn):
            self._app._managers_['schedules'][key] = {
                'timer': timer,
                'fn': dill.dumps(fn),
                'startTimer': startTimer,
                'expected_repetition_num': expected_repetition_num,
                'total_repetition_num': 0,
                'auto_remove': auto_remove,
                'active': True
            }
            return fn
        return decorator

    @overload
    def remove(self, fn: Callable):
        '''
        通过函数删除计划。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(datetime.timedelta(days = 1))
        async def task():
            print('Hello World.')

        app.scheduler.remove(task)
        ```
        '''

    @overload
    def remove(self, key: str):
        '''
        通过key删除计划。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(datetime.timedelta(days = 1), key = 'myTask')
        async def task():
            print('Hello World.')

        app.scheduler.remove('myTask')
        ```
        '''

    def remove(self, arg1: Callable | str):
        if isinstance(arg1, Callable):
            for key, value in self.tasks.items():
                if value.fn == arg1:
                    del self._app._managers_['schedules'][key]
        elif isinstance(arg1, str):
            del self._app._managers_['schedules'][arg1]

    @overload
    def get_task(self, fn: Callable) -> ScheduleTask:
        '''
        通过函数获取`ScheduleTask`。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(datetime.timedelta(days = 1))
        async def task():
            print('Hello World.')

        myTask = app.scheduler.get_task(task)
        ```
        '''

    @overload
    def get_task(self, key: str) -> ScheduleTask:
        '''
        通过key获取`ScheduleTask`，`ScheduleTask`请查看[Schedule](../Schedule.md)。

        ```python
        import datetime

        from CheeseAPI import app

        @app.scheduler.add(datetime.timedelta(days = 1), key = 'myTask')
        async def task():
            print('Hello World.')

        myTask = app.scheduler.get_task('myTask')
        ```
        '''

    def get_task(self, arg1: Callable | str) -> ScheduleTask:
        if isinstance(arg1, Callable):
            for key, value in self.tasks.items():
                if value.fn == arg1:
                    return value
        elif isinstance(arg1, str):
            return ScheduleTask(arg1, key)

    @property
    def tasks(self) -> Dict[str, ScheduleTask]:
        '''
        【只读】 所有的任务。

        未指定key的任务会自动分配一个uuid字符串为key。
        '''

        return {
            key: ScheduleTask(self._app, key) for key in self._app._managers_['schedules'].keys()
        }
