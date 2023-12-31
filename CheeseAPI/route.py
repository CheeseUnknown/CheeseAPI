import re, uuid, http
from typing import Callable, Dict, List, Tuple, Any, Literal
from urllib.parse import unquote

patterns: Dict[str, re.Pattern] = {
    'uuid': {
        'pattern': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
        'type': uuid.UUID
    },
    'float': {
        'pattern': r'[-+]?[0-9]+.[0-9]+',
        'type': float
    },
    'int': {
        'pattern': r'[-+]?[0-9]+',
        'type': int
    },
    'str': {
        'pattern': r'.+',
        'type': str
    }
}

class PathNode:
    def __init__(self):
        self.children: Dict[str, PathNode] = None
        self.key: str | None = None
        self.methods: Dict[str, Tuple[str, Callable]] | None = None

class Path:
    def __init__(self):
        self.root: PathNode = PathNode()

    def insert(self, path: str, func: Callable, methods: List[http.HTTPMethod | str]):
        for method in methods:
            if method != 'WEBSOCKET':
                method = http.HTTPMethod(method)

        node = self.root

        for part in path.split('/')[1:]:
            if not node.children:
                node.children = {}

            if re.match(r'<\w+:\w+>', part):
                part = part[1:-1].split(':')
                _part = f'<:{part[1]}>'
                if _part not in node.children:
                    node.children[_part] = PathNode()
                node.children[_part].key = part[0]
                part = _part
            else:
                if part not in node.children:
                    node.children[part] = PathNode()
            node = node.children[part]

        if not node.methods:
            node.methods = {}
        for method in methods:
            node.methods[method] = path, func

    def match(self, path: str, method: http.HTTPMethod | Literal['WEBSOCKET']) -> Tuple[Callable, Dict[str, Any]]:
        paths = path.split('/')[1:]
        if paths[-1] == '' and path != '/':
            paths = paths[:-1]

        results = self._match(self.root, paths, {})
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
                kwargs[p[0]] = patterns[p[1]]['type'](unquote(paths[i]))

        return results[1], kwargs

    def _match(self, node: PathNode, paths: List[str], results: Dict[http.HTTPMethod, Tuple[str, Callable]]) -> Dict[http.HTTPMethod, Tuple[str, Callable]]:
        if paths and node.children:
            if paths[0] in node.children:
                results = self._match(node.children[paths[0]], paths[1:], results)
            paths[0] = unquote(paths[0])
            for key, value in patterns.items():
                if re.fullmatch(value['pattern'], paths[0]) and f'<:{key}>' in node.children:
                    results = self._match(node.children[f'<:{key}>'], paths[1:], results)

        if not paths and node.methods:
            for key, value in node.methods.items():
                if key not in results:
                    results[key] = value
        return results

paths: Path = Path()

class Route:
    def __init__(self, prefix: str = ''):
        self.prefix: str = prefix

    def __call__(self, path: str, methods: List[ http.HTTPMethod | str ]):
        def decorator(func):
            paths.insert(self.prefix + path, func, methods)
            return func
        return decorator

    def get(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.GET ])
            return func
        return decorator

    def post(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.POST ])
            return func
        return decorator

    def delete(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.DELETE ])
            return func
        return decorator

    def put(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.PUT ])
            return func
        return decorator

    def patch(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.PATCH ])
            return func
        return decorator

    def trace(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.TRACE ])
            return func
        return decorator

    def options(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.OPTIONS ])
            return func
        return decorator

    def head(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.HEAD ])
            return func
        return decorator

    def connect(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.CONNECT ])
            return func
        return decorator

    def websocket(self, path: str):
        def decorator(cls):
            paths.insert(self.prefix + path, cls, [ 'WEBSOCKET' ])
            return cls
        return decorator
