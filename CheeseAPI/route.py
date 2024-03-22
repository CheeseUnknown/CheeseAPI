import uuid, re, http
from typing import Dict, Tuple, Callable, List, Any, Literal
from urllib.parse import unquote

class RouteNode:
    def __init__(self):
        self.children: Dict[str, RouteNode] = {}
        self.key: str | None = None
        self.methods: Dict[str, Tuple[str, Callable]] = {}

class RouteBus:
    def __init__(self):
        self.patterns: List[Dict[str, Any]] = [
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

    def addPattern(self, key: str, pattern: re.Pattern, type: object, weight: int):
        self.patterns.append({
            'key': key,
            'pattern': pattern,
            'type': type,
            'weight': weight
        })
        self.patterns = sorted(self.patterns, key = lambda x: x['weight'], reverse = True)

    def _insert(self, path: str, func: Callable, methods: List[http.HTTPMethod | str]):
        for method in methods:
            if method != 'WEBSOCKET':
                method = http.HTTPMethod(method)

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
        for method in methods:
            node.methods[method] = path, func

    def _match(self, path: str, method: http.HTTPMethod | Literal['WEBSOCKET']) -> Tuple[Callable, Dict[str, Any]]:
        paths = path.split('/')[1:]
        if paths[-1] == '' and path != '/':
            paths = paths[:-1]

        results = self.__match(self._node, paths, {})
        if not results:
            raise KeyError(0)
        if method not in results:
            raise KeyError(1)
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
            for key, value in node.methods.items():
                if key not in results:
                    results[key] = value
        return results

class Route:
    def __init__(self, prefix: str = ''):
        self.prefix: str = prefix

    def __call__(self, path: str, methods: List[ http.HTTPMethod | str ]):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, methods)
            return func
        return decorator

    def get(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.GET ])
            return func
        return decorator

    def post(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.POST ])
            return func
        return decorator

    def delete(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.DELETE ])
            return func
        return decorator

    def put(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.PUT ])
            return func
        return decorator

    def patch(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.PATCH ])
            return func
        return decorator

    def trace(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.TRACE ])
            return func
        return decorator

    def options(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.OPTIONS ])
            return func
        return decorator

    def head(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.HEAD ])
            return func
        return decorator

    def connect(self, path: str):
        def decorator(func):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, func, [ http.HTTPMethod.CONNECT ])
            return func
        return decorator

    def websocket(self, path: str):
        def decorator(cls):
            from CheeseAPI.app import app

            app.routeBus._insert(self.prefix + path, cls, [ 'WEBSOCKET' ])
            return cls
        return decorator
