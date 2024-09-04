import uuid, re, http
from typing import Dict, Tuple, Callable, List, Any, Literal, overload, TYPE_CHECKING, Type
from urllib.parse import unquote

from CheeseAPI.exception import Route_404_Exception, Route_405_Exception

if TYPE_CHECKING:
    from CheeseAPI.websocket import WebsocketServer

class RouteNode:
    def __init__(self):
        self.children: Dict[str, RouteNode] = {}
        self.key: str | None = None
        self.methods: Dict[str, Tuple[str, Callable]] = {}

class RouteBus:
    def __init__(self):
        self._patterns: List[Dict[str, Any]] = [
            {
                'key': 'uuid',
                'pattern': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
                'type': uuid.UUID,
                'weight': 10
            },
            {
                'key': 'float',
                'pattern': r'[-+]?[0-9]+\.[0-9]+',
                'type': float,
                'weight': 10
            },
            {
                'key': 'int',
                'pattern': r'[-+]?[0-9]+',
                'type': int,
                'weight': 10
            },
            {
                'key': 'str',
                'pattern': r'.+',
                'type': str,
                'weight': 0
            }
        ]
        self._node: RouteNode = RouteNode()

    def addPattern(self, key: str, pattern: str, type: object | Callable, weight: int):
        '''
        新增动态路由匹配条件。

        - Arg
            - key: 在动态路由中的key。

            - pattern: 使用正则匹配动态路由的字符串。

            - type: 若匹配成功，则会将字符串转为该类；请确保该类可以使用`Xxx(value: str)`进行转换，或是一个返回值为该类的函数。

            - weight: 匹配优先级的权重；更高的权重意味着优先级更高的匹配，若匹配成功则不会继续匹配。
        '''

        self.patterns.append({
            'key': key,
            'pattern': pattern,
            'type': type,
            'weight': weight
        })
        self.patterns = sorted(self.patterns, key = lambda x: x['weight'], reverse = True)

    def _insert(self, path: str, fn: Callable, methods: List[http.HTTPMethod | str]):
        methods = [http.HTTPMethod(method) if method != 'WEBSOCKET' else method for method in methods]
        node = self._node

        for part in path.split('/')[1:]:
            if re.match(r'<\w+:\w+>', part):
                part = part[1:-1].split(':')
                _part = f'<:{part[1]}>'
                if _part not in node.children:
                    node.children[_part] = RouteNode()
                node.children[_part].key = part[0]
                part = _part
            else:
                if part not in node.children:
                    node.children[part] = RouteNode()
            node = node.children[part]

        if not node.methods:
            node.methods = {}
        node.methods.update({
            method: (path, fn) for method in methods
        })

    def _match(self, path: str, method: http.HTTPMethod | Literal['WEBSOCKET']) -> Tuple[Callable, Dict[str, Any]]:
        paths = path.split('/')[1:]
        if paths[-1] == '' and path != '/':
            paths = paths[:-1]

        results = self.__match(self._node, paths, {})
        if not results:
            raise Route_404_Exception()
        if method not in results:
            raise Route_405_Exception()
        results = results[method]
        kwargs = {}
        _paths = results[0].split('/')
        for i in range(len(paths)):
            if re.match(r'<.*?:.*?>', _paths[i + 1]):
                p = _paths[i + 1][1:-1].split(':')
                for pattern in self.patterns:
                    if pattern['key'] == p[1]:
                        kwargs[p[0]] = pattern['type'](unquote(paths[i]))
                        break

        return results[1], kwargs

    def __match(self, node: RouteNode, paths: List[str], results: Dict[http.HTTPMethod, Tuple[str, Callable]]) -> Dict[http.HTTPMethod, Tuple[str, Callable]]:
        if paths and node.children:
            if paths[0] in node.children:
                results = self.__match(node.children[paths[0]], paths[1:], results)
            paths[0] = unquote(paths[0])
            for pattern in self.patterns:
                if re.fullmatch(pattern['pattern'], paths[0]) and f'<:{pattern["key"]}>' in node.children:
                    results = self.__match(node.children[f'<:{pattern["key"]}>'], paths[1:], results)
                    break

        if not paths and node.methods:
            results.update({
                key: value for key, value in node.methods.items() if key not in results
            })
        return results

    @property
    def patterns(self) -> List[Dict[str, Any]]:
        '''
        【只读】 可匹配的动态路由参数。
        '''

        return self._patterns

class Route:
    def __init__(self, prefix: str = ''):
        self.prefix: str = prefix

    @overload
    def __call__(self, path: str, methods: List[ http.HTTPMethod | str ]):
        ...

    @overload
    def __call__(self, path: str, methods: List[ http.HTTPMethod | str ], fn: Callable):
        ...

    def __call__(self, path: str, methods: List[ http.HTTPMethod | str ], fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, methods)
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, methods)
            return fn
        return wrapper

    @overload
    def get(self, path: str):
        ...

    @overload
    def get(self, path: str, fn: Callable):
        ...

    def get(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.GET ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.GET ])
            return fn
        return wrapper

    @overload
    def post(self, path: str):
        ...

    @overload
    def post(self, path: str, fn: Callable):
        ...

    def post(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.POST ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.POST ])
            return fn
        return wrapper

    @overload
    def delete(self, path: str):
        ...

    @overload
    def delete(self, path: str, fn: Callable):
        ...

    def delete(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.DELETE ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.DELETE ])
            return fn
        return wrapper

    @overload
    def put(self, path: str):
        ...

    @overload
    def put(self, path: str, fn: Callable):
        ...

    def put(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.PUT ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.PUT ])
            return fn
        return wrapper

    @overload
    def patch(self, path: str):
        ...

    @overload
    def patch(self, path: str, fn: Callable):
        ...

    def patch(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.PATCH ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.PATCH ])
            return fn
        return wrapper

    @overload
    def trace(self, path: str):
        ...

    @overload
    def trace(self, path: str, fn: Callable):
        ...

    def trace(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.TRACE ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.TRACE ])
            return fn
        return wrapper

    @overload
    def options(self, path: str):
        ...

    @overload
    def options(self, path: str, fn: Callable):
        ...

    def options(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.OPTIONS ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.OPTIONS ])
            return fn
        return wrapper

    @overload
    def head(self, path: str):
        ...

    @overload
    def head(self, path: str, fn: Callable):
        ...

    def head(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.HEAD ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.HEAD ])
            return fn
        return wrapper

    @overload
    def connect(self, path: str):
        ...

    @overload
    def connect(self, path: str, fn: Callable):
        ...

    def connect(self, path: str, fn: Callable | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.CONNECT ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ http.HTTPMethod.CONNECT ])
            return fn
        return wrapper

    @overload
    def websocket(self, path: str):
        ...

    @overload
    def websocket(self, path: str, fn: 'WebsocketServer'):
        ...

    def websocket(self, path: str, fn: Type['WebsocketServer'] | None = None):
        from CheeseAPI.app import app

        if fn:
            app.routeBus._insert(self.prefix + path, fn, [ 'WEBSOCKET' ])
            return

        def wrapper(fn):
            app.routeBus._insert(self.prefix + path, fn, [ 'WEBSOCKET' ])
            return fn
        return wrapper
