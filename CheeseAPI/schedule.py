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
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'total_repetition_num': 0
        }

    @property
    def timer(self) -> datetime.timedelta:
        return self._app._managers['schedules'][self.key]['timer']

    @timer.setter
    def timer(self, value: datetime.timedelta):
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'timer': value
        }

    @property
    def fn(self) -> Callable:
        return dill.loads(self._app._managers['schedules'][self.key]['fn'])

    @fn.setter
    def fn(self, value: Callable):
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'fn': dill.dumps(value)
        }

    @property
    def startTimer(self) -> datetime.datetime:
        return self._app._managers['schedules'][self.key]['startTimer']

    @startTimer.setter
    def startTimer(self, value: datetime.datetime):
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'startTimer': value
        }

        if self.auto_remove and self.is_expired:
            del self._app._managers['schedules'][self.key]

    @property
    def auto_remove(self) -> bool:
        return self._app._managers['schedules'][self.key]['auto_remove']

    @auto_remove.setter
    def auto_remove(self, value: bool):
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'auto_remove': value
        }

        if self.auto_remove and self.is_expired:
            del self._app._managers['schedules'][self.key]

    @property
    def active(self) -> bool:
        return self._app._managers['schedules'][self.key]['active']

    @active.setter
    def active(self, value: bool):
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'active': value
        }

        if self.auto_remove and self.is_expired:
            del self._app._managers['schedules'][self.key]

    @property
    def expected_repetition_num(self) -> int:
        return self._app._managers['schedules'][self.key]['expected_repetition_num']

    @expected_repetition_num.setter
    def expected_repetition_num(self, value: int):
        self._app._managers['schedules'][self.key] = {
            **self._app._managers['schedules'][self.key],
            'expected_repetition_num': value
        }

        if self.auto_remove and self.is_expired:
            del self._app._managers['schedules'][self.key]

    @property
    def total_repetition_num(self) -> int:
        return self._app._managers['schedules'][self.key]['total_repetition_num']

    @property
    def remaining_repetition_num(self) -> int:
        if self.expected_repetition_num == 0:
            return -1
        return self.expected_repetition_num - self.total_repetition_num

    @property
    def is_unexpired(self) -> bool:
        if self.expected_repetition_num == 0:
            return True

        return self.startTimer + self.timer * (self.expected_repetition_num + 1) >= datetime.datetime.now()

    @property
    def is_expired(self) -> bool:
        return not self.is_unexpired

class Scheduler:
    def __init__(self, app: 'App'):
        self._app: 'App' = app

    @overload
    def add(self, timer: datetime.timedelta, fn: Callable, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False):
        ...

    @overload
    def add(self, timer: datetime.timedelta, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False):
        ...

    def add(self, timer: datetime.timedelta, fn: Callable | None = None, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False):
        if not key:
            key = str(uuid.uuid4())

        if not startTimer:
            startTimer = datetime.datetime.now()

        if fn:
            self._app._managers['schedules'][key] = {
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
            self._app._managers['schedules'][key] = {
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
        ...

    @overload
    def remove(self, key: str):
        ...

    def remove(self, arg1: Callable | str):
        if isinstance(arg1, Callable):
            for key, value in self.tasks.items():
                if value.fn == arg1:
                    del self._app._managers['schedules'][key]
        elif isinstance(arg1, str):
            del self._app._managers['schedules'][arg1]

    @overload
    def get_task(self, fn: Callable) -> ScheduleTask:
        ...

    @overload
    def get_task(self, key: str) -> ScheduleTask:
        ...

    def get_task(self, arg1: Callable | str) -> ScheduleTask:
        if isinstance(arg1, Callable):
            for key, value in self.tasks.items():
                if value.fn == arg1:
                    return value
        elif isinstance(arg1, str):
            return ScheduleTask(arg1, key)

    @property
    def tasks(self) -> Dict[str, ScheduleTask]:
        return {
            key: ScheduleTask(self._app, key) for key in self._app._managers['schedules'].keys()
        }
