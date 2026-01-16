import __init__
from CheeseAPI import CheeseAPI

app = CheeseAPI(exclude_modules = ['examples', 'tests'])

def task1(*args, **kwargs):
    print('Task 1: THREAD')

def task2(*args, **kwargs):
    print('Task 2: PROCESS')

async def task3(*args, **kwargs):
    print('Task 3: ASYNC')

@app.signal.after_server_start.connect()
def tasks():
    app.scheduler.add(task1, interval_time = 1)
    app.scheduler.add(task2, interval_time = 1, run_type = 'PROCESS')

@app.signal.after_worker_start.connect()
async def async_tasks(*, is_first: bool):
    if is_first:
        await app.scheduler.async_add(task3, interval_time = 1, auto_remove = True, expected_run_num = 1)

if __name__ == '__main__':
    app.start()
