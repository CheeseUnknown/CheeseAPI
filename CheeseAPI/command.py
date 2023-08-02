import argparse, time, os, traceback, json, shutil, importlib, importlib.util

import CheeseLog, uvicorn, CheeseType, CheeseType.network, uvicorn.importer

from .module import Module, LocalModule

def command():
    from .app import app
    from .cSignal import signal

    parser = argparse.ArgumentParser()
    parser.add_argument('--app', nargs = '?', default = 'app:app', help = '服务器本服务【默认值：app:app】')
    parser.add_argument('--host', nargs = '?', default = '127.0.0.1', help = '服务器地址【默认值：127.0.0.1】')
    parser.add_argument('--port', type = int, nargs = '?', default = 5214, help = '端口号【默认值：5214】')
    parser.add_argument('--reload', action='store_true', help = '热更新。与workers冲突【默认值：False】')
    parser.add_argument('--workers', type = int, nargs = '?', default = 1, help = 'workers为0时会自动设置为cpu核数*2。与reload冲突【默认值：1】')
    parser.add_argument('--log_path', nargs = '?', default = '/logs/', help = '日志文件夹的相对路径【默认值：/logs/】')
    parser.add_argument('--log_filename', nargs = '?', default = False, help = '日志文件名。当值为True时，自动设置为%%Y_%%m_%%d-%%H_%%M_%%S.log；当值为False，关闭日志文件记录；自定义文件名也是允许的【默认值：True】')
    args = parser.parse_args()

    startTimer: float = time.time()

    _app = args.app
    host = CheeseType.network.IPv4(args.host)
    port = CheeseType.network.Port(args.port)
    reload = CheeseType.Bool(args.reload)
    workers = CheeseType.NonNegativeInt(args.workers)
    log_path = args.log_path
    try:
        log_filename = CheeseType.Bool(args.log_filename)
    except:
        ...

    if reload:
        workers = 1

    app.workspace.LOG_PATH = log_path
    app.server.LOG_FILENAME = log_filename
    app.server.HOST = host
    app.server.PORT = port
    app.server.IS_RELOAD = reload
    app.server.WORKERS = workers

    if os.path.exists(app.workspace.BASE_PATH + '/.cache'):
        shutil.rmtree(app.workspace.BASE_PATH + '/.cache')
    if workers != 1:
        os.makedirs(app.workspace.BASE_PATH + '/.cache', exist_ok = True)
        with open(app.workspace.BASE_PATH + '/.cache/config.json', "w") as f:
            json.dump({
                'workers': 0,
                'app': _app,
                'workspace': {
                    'LOG_PATH': log_path
                },
                'server': {
                    'HOST': host,
                    'PORT': port,
                    'IS_RELOAD': reload,
                    'WORKERS': workers,
                    'LOG_FILENAME': log_filename
                }
            }, f)

    CheeseLog.starting(f'Started CheeseAPI master process {os.getpid()}', f'Started CheeseAPI master process \033[34m{os.getpid()}\033[0m')
    CheeseLog.starting('The application starts loading...')

    CheeseLog.starting('''System information:
system: ''' + {
'WINDOWS': 'Windows',
'LINUX': 'Linux',
'MACOS': 'MacOS',
'OTHER': 'Other'
}[app.system.SYSTEM.value] + f'''
python version: {app.system.PYTHON_VERSION}''' + (f'''
CheeseAPI version: {app.system.CHEESEAPI_VERSION}''' if app.system.CHEESEAPI_VERSION is not None else ''))

    CheeseLog.starting(f'''Workspace information:
CheeseAPI path: {app.workspace.CHEESEAPI_PATH}
base path: {app.workspace.BASE_PATH}''' + (f'''
static path: .{app.workspace.STATIC_PATH}''' if app.server.STATIC_PATH is not False else '') + f'''
media path: .{app.workspace.MEDIA_PATH}''' + (f'''
log path: .{app.workspace.LOG_PATH}''' if app.server.LOG_FILENAME is not False else ''), f'''Workspace information:
CheeseAPI path: \033[4;36m{app.workspace.CHEESEAPI_PATH}\033[0m
base path: \033[4;36m{app.workspace.BASE_PATH}\033[0m''' + (f'''
static path: \033[4;36m.{app.workspace.STATIC_PATH}\033[0m''' if app.server.STATIC_PATH is not False else '') + f'''
media path: \033[4;36m.{app.workspace.MEDIA_PATH}\033[0m''' + (f'''
log path: \033[4;36m.{app.workspace.LOG_PATH}\033[0m''' if app.server.LOG_FILENAME is not False else ''))

    CheeseLog.starting(f'''Server information:
host: {app.server.HOST}
port: {app.server.PORT}
workers: {app.server.WORKERS}
is reload: {app.server.IS_RELOAD}
is debug: {app.server.IS_DEBUG}
is request logged: {app.server.IS_REQUEST_LOGGED}''' + (f'''
static path: {app.server.STATIC_PATH}''' if app.server.STATIC_PATH is not False else '') + (f'''
current log file path: .{app.logger.filePath[len(app.workspace.BASE_PATH):]}''' if app.server.LOG_FILENAME is not False else ''), f'''Server information:
host: \033[36m{app.server.HOST}\033[0m
port: \033[34m{app.server.PORT}\033[0m
workers: \033[34m{app.server.WORKERS}\033[0m
is reload: \033[34m{app.server.IS_RELOAD}\033[0m
is debug: \033[34m{app.server.IS_DEBUG}\033[0m
is request logged: \033[34m{app.server.IS_REQUEST_LOGGED}\033[0m''' + (f'''
static path: \033[34m{app.server.STATIC_PATH}\033[0m''' if app.server.STATIC_PATH is not False else '') + (f'''
current log file path: \033[4;36m.{app.logger.filePath[len(app.workspace.BASE_PATH):]}\033[0m''' if app.server.LOG_FILENAME is not False else ''))

    CheeseLog.starting(f'The server running on http://{app.server.HOST}:{app.server.PORT}', f'The server running on \033[4;36mhttp://{app.server.HOST}:{app.server.PORT}\033[0m')

    import sys
    sys.path.append(os.getcwd())
    app = __import__(_app.split(':')[0]).app

    _modules = set()
    if len(app.modules):
        CheeseLog.starting(f'Modules:\n{" | ".join(app.modules)}')
    for module in app.modules:
        _modules.add(Module(_modules, module))
    app.modules = _modules

    if app.localModules is True:
        app.localModules = set()
        for folderName in os.listdir(app.workspace.BASE_PATH):
            if folderName[0] == '.':
                continue
            if folderName in app.exclude_localModules:
                continue
            folderPath = os.path.join(app.workspace.BASE_PATH, folderName)
            if os.path.isdir(folderPath) and folderPath not in [ app.workspace.BASE_PATH + app.workspace.STATIC_PATH[:-1], app.workspace.BASE_PATH + app.workspace.MEDIA_PATH[:-1], app.workspace.BASE_PATH + app.workspace.LOG_PATH[:-1], app.workspace.BASE_PATH + '/__pycache__' ]:
                app.localModules.add(folderName)
    if len(app.localModules):
        CheeseLog.starting(f'Local modules:\n{" | ".join(app.localModules)}')
    _localModules = set()
    for module in app.localModules:
        _localModules.add(LocalModule(app.workspace.BASE_PATH, module))
    app.localModules = _localModules

    if signal.receiver('server_startingHandle'):
        signal.send('server_startingHandle')
    for server_startingHandle in app.server_startingHandles:
        server_startingHandle()

    try:
        uvicorn.run(
            _app,
            host = app.server.HOST,
            port = app.server.PORT,
            reload = app.server.IS_RELOAD,
            workers = app.server.WORKERS,
            log_level = 'critical',
            app_dir = app.workspace.BASE_PATH
        )
    except:
        CheeseLog.error(f'server startup failed\n{traceback.format_exc()}'[:-1])

    if signal.receiver('server_endingHandle'):
        signal.send('server_endingHandle')
    for server_endingHandle in app.server_endingHandles:
        server_endingHandle()

    print('')
    CheeseLog.ending('The application tries to stop...')
    runningTime = time.time() - startTimer
    endingMessage = 'The application stopped, running '
    endingColorfulMessage = 'The application stopped, running '
    days = int(runningTime // 86400)
    if days:
        endingMessage += f'{days} days '
        endingColorfulMessage += f'\033[34m{days}\033[0m days '
    hours = int(runningTime % 24 // 3600)
    if days or hours:
        endingMessage += f'{hours} hours '
        endingColorfulMessage += f'\033[34m{hours}\033[0m hours '
    minutes = int(runningTime % 3600 // 60)
    if days or hours or minutes:
        endingMessage += f'{minutes} minutes '
        endingColorfulMessage += f'\033[34m{minutes}\033[0m minutes '
    endingMessage += '{:.6f} seconds'.format(runningTime % 60)
    endingColorfulMessage += '\033[34m{:.6f}\033[0m seconds'.format(runningTime % 60)
    CheeseLog.ending(endingMessage, endingColorfulMessage)
    if app.logger.is_alive():
        app.logger.stop()
