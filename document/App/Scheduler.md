# **Scheduler**

任务调度；在服务器运行时定时执行函数。

触发时间的准确度受`app.server.intervalTime`以及`app.signal.server_running`、`app.signal.worker_running`两个插槽影响。判断间隔时间过长或插槽内函数响应过慢都会影响任务的触发时机。

`app.scheduler`是跨进程的，它可以很好的在多worker环境下工作。

## **`app.scheduler.tasks: Dict[str, ScheduleTask]`**

【只读】 所有的任务，`ScheduleTask`请查看[Schedule](../Schedule.md)。

未指定key的任务会自动分配一个字符串为key。

## **`app.scheduler.add(timer: datetime.timedelta, fn: Callable, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False, mode: Literal['multiprocessing', 'threading', 'asyncio'] = 'multiprocessing', intervalTime: float | None = None)`**

通过函数添加一个任务。

任务函数必须为协程函数。

```python
import datetime

from CheeseAPI import app

async def task(lastReturn, *, intervalTime: float, **_):
    print('Hello World.')

app.scheduler.add(datetime.timedelta(days = 1), task)
```

- **参数**

    - **timer**

        触发任务的间隔时间。

    - **startTimer**

        为该计划设定一个开始时间，而不是使用当前时间。

    - **expected_repetition_num**

        期望的重复次数，0代表无限重复。

    - **auto_remove**

        若`expected_repetition_num > 0`且当前计划过期，是否自动删除该计划。

    - **mode**

        运行的模式是进程、线程还是协程。

    - **intervalTime**

        最小检查间隔，仅在`mode == 'threading'`或`mode == 'multiprocessing'`时生效。默认为`app.server.intervalTime`。

## **`app.scheduler.add(timer: datetime.timedelta, *, key: str | None = None, startTimer: datetime.datetime | None = None, expected_repetition_num: int = 0, auto_remove: bool = False, mode: Literal['multiprocessing', 'threading', 'asyncio'] = 'multiprocessing', intervalTime: float | None = None)`**

通过装饰器添加一个任务。

任务函数必须为协程函数。

```python
import datetime

from CheeseAPI import app

@app.scheduler.add(timer = datetime.timedelta(days = 1))
async def task(lastReturn, *, intervalTime: float, **_):
    print('Hello World.')
```

- **参数**

    - **timer**

        触发任务的间隔时间。

    - **startTimer**

        为该计划设定一个开始时间，而不是使用当前时间。

    - **expected_repetition_num**

        期望的重复次数，0代表无限重复。

    - **auto_remove**

        若`expected_repetition_num > 0`且当前计划过期，是否自动删除该计划。

    - **mode**

        运行的模式是进程、线程还是协程。

    - **intervalTime**

        最小检查间隔，仅在`mode == 'threading'`或`mode == 'multiprocessing'`时生效。默认为`app.server.intervalTime`。

- **回调函数参数**

    - **lastReturn**

        上一次触发时的返回值。

    - **intervalTime**

        距离上一次触发的间隔时间。

## **`app.scheduler.remove(fn: Callable)`**

通过函数删除计划。

```python
import datetime

from CheeseAPI import app

@app.scheduler.add(timer = datetime.timedelta(days = 1))
async def task(lastReturn, *, intervalTime: float, **_):
    print('Hello World.')

app.scheduler.remove(task)
```

## **`app.scheduler.remove(key: str)`**

通过key删除计划。

```python
import datetime

from CheeseAPI import app

@app.scheduler.add(timer = datetime.timedelta(days = 1), key = 'myTask')
async def task(lastReturn, *, intervalTime: float, **_):
    print('Hello World.')

app.scheduler.remove('myTask')
```

## **`app.scheduler.get_task(fn: Callable) -> ScheduleTask`**

通过函数获取`ScheduleTask`，`ScheduleTask`请查看[Schedule](../Schedule.md)。

```python
import datetime

from CheeseAPI import app

@app.scheduler.add(timer = datetime.timedelta(days = 1))
async def task(lastReturn, *, intervalTime: float, **_):
    print('Hello World.')

myTask = app.scheduler.get_task(task)
```

## **`app.scheduler.get_task(key: str) -> ScheduleTask`**

通过key获取`ScheduleTask`，`ScheduleTask`请查看[Schedule](../Schedule.md)。

```python
import datetime

from CheeseAPI import app

@app.scheduler.add(timer = datetime.timedelta(days = 1), key = 'myTask')
async def task(lastReturn, *, intervalTime: float, **_):
    print('Hello World.')

myTask = app.scheduler.get_task('myTask')
```
