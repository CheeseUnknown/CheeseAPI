import multiprocessing, os
from typing import Dict, Any, List

from CheeseAPI.text import Text
from CheeseAPI.server import Server
from CheeseAPI.workspace import Workspace
from CheeseAPI.handle import Handle
from CheeseAPI.signal import _Signal
from CheeseAPI.route import Route, RouteBus
from CheeseAPI.cors import Cors
from CheeseAPI.schedule import Scheduler

class App:
    def __init__(self):
        self.manager = multiprocessing.Manager()

        self._server: Server = Server(self)
        self._workspace: Workspace = Workspace(self)
        self._signal: _Signal = _Signal(self)
        self._scheduler: Scheduler = Scheduler(self)
        self._managers: Dict[str, Any] = {}
        self._g: Dict[str, Any] = {
            'startTime': None
        }
        self._route: Route = Route()
        self._routeBus: RouteBus = RouteBus()
        self._cors: Cors = Cors()

        self._modules: List[str] = []
        self._localModules: List[str] = []
        self._exclude_localModules: List[str] = []
        self._preferred_localModules: List[str] = []

        self._text: Text = Text(self)
        self._managers_: Dict[str, Any] = {
            'server.workers': self.manager.Value(int, 0),
            'lock': self.manager.Lock(),
            'schedules': self.manager.dict()
        }
        self._handle: Handle = Handle(self)

        # 初始化本地模块
        for foldername in os.listdir(self.workspace.base):
            if foldername[0] == '.' or foldername == '__pycache__':
                continue

            folderPath = os.path.join(self.workspace.base, foldername)
            if not os.path.isdir(folderPath):
                continue

            staticPath = os.path.join(self.workspace.base, self.workspace.static)
            if self.workspace.static and os.path.exists(staticPath) and os.path.samefile(folderPath, staticPath):
                continue

            logPath = os.path.join(self.workspace.base, self.workspace.log)
            if self.workspace.log and os.path.exists(logPath) and os.path.samefile(folderPath, logPath):
                continue

            self.localModules.append(foldername)

    def run(self):
        self._handle.server_start()

    @property
    def server(self) -> Server:
        '''
        【只读】 服务器运行时需要的配置。
        '''

        return self._server

    @property
    def workspace(self) -> Workspace:
        '''
        【只读】 工作目录相关配置。
        '''

        return self._workspace

    @property
    def signal(self) -> _Signal:
        '''
        【只读】 插槽。
        '''

        return self._signal

    @property
    def scheduler(self) -> Scheduler:
        '''
        【只读】 任务调度者。
        '''

        return self._scheduler

    @property
    def managers(self) -> Dict[str, Any]:
        '''
        【只读】 多worker间的同步数据。

        ```python
        from CheeseAPI import app

        app.managers['myLock'] = app.manager.Lock()

        app.run()
        ```

        在任意worker中，都可以读写其value，但无法添加或删除`app.managers`中的key，这是不同步的操作！

        ```python
        from CheeseAPI import app, Response

        @app.route.get('/')
        async def index(**kwargs):
            with app.managers['lock']:
                return Response('这里是CheeseAPI！')
        ```
        '''

        return self._managers

    @property
    def g(self) -> Dict[str, Any]:
        '''
        【只读】 在server启动时就固定的数据，不需要在server运行时修改。

        ```python
        from CheeseAPI import app

        app.g['my_project_version'] = '1.0.0'

        app.run()
        ```

        - `startTime: None | float = None`

            在server启动时会自动赋值为`float`类型的时间戳。
        '''

        return self._g

    @property
    def route(self) -> Route:
        '''
        【只读】 无前缀的路由。
        '''

        return self._route

    @property
    def routeBus(self) -> RouteBus:
        '''
        【只读】 路由总线，管理所有的路由。
        '''

        return self._routeBus

    @property
    def cors(self) -> Cors:
        '''
        【只读】 跨域管理。
        '''

        return self._cors

    @property
    def modules(self) -> List[str]:
        '''
        【只读】 加载的插件模块，这部分一般由第三方开发者开发，具体的使用方法最终应参考该模块文档。

        请确保该模块是支持CheeseAPI的，并且已经下载至本地仓库：

        ```
        pip install Xxx
        ```

        ```python
        from CheeseAPI import app

        app.modules.extends([ 'Xxx' ])

        app.run()
        ```

        若该插件模块允许分别加载子模块，可如此导入：

        ```python
        from CheeseAPI import app

        app.modules.extends([ 'Xxx.module1', 'Xxx.module2' ])

        app.run()
        ```

        最终导入的插件模块都将在启动时的信息中展示。
        '''

        return self._modules

    @property
    def localModules(self) -> List[str]:
        '''
        【只读】 前提：所有本地模块未使用代码导入。

        本地模块都是基于`app.workspace.base`路径的文件夹。

        默认所有本地模块都会加载，不能确保模块的加载顺序。

        若自定义加载的本地模块，可以强制规定加载顺序，并忽略其他未加入的模块：

        当前文件结构：

        ```
        | - Module1
            | - ...
        | - Module2
            | - ...
        | - app.py
        ```

        ```python
        from CheeseAPI import app

        app.localModules.extends([ 'Module1' ])

        app.run()
        ```

        最终导入的本地模块都将在启动时的信息中展示。
        '''

        return self._localModules

    @property
    def exclude_localModules(self) -> List[str]:
        '''
        【只读】 前提：所有本地模块未使用代码导入。

        忽略的本地模块；静态文件路径和日志路径会自动忽略，不需要额外添加。

        优先级最高，该列表中的模块名若存在于`app.localModules`中，则在加载过程中会忽略该模块。

        多用于`app.localModules`为自动导入的时候，可对少数模块进行过滤。

        ```python
        from CheeseAPI import app

        app.exclude_localModules.extends([ 'Module1' ]) # 若有Module1模块，则不会加载它

        app.run()
        ```
        '''

        return self._exclude_localModules

    @property
    def preferred_localModules(self) -> List[str]:
        '''
        【只读】 前提：所有本地模块未使用代码导入。

        优先加载的本地模块，按列表顺序加载。

        优先级低于`app.exclude_localModules`，其中的模块名仍优先忽略。

        未存在于`app.localModules`的模块仍然不会加载。

        ```python
        from CheeseAPI import app

        app.preferred_localModules.extends([ 'Module1', 'Module2' ]) # 若模块名都存在，则先加载Module1，再加载Module2

        app.run()
        ```
        '''

        return self._preferred_localModules

app: App = App()
