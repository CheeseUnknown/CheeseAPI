import re, uuid, http
from typing import Callable, Dict, List, Tuple, Any

patterns: Dict[str, re.Pattern] = {
    'str': {
        'pattern': r'.+',
        'type': str
    },
    'int': {
        'pattern': r'[-+]?[0-9]+',
        'type': int
    },
    'float': {
        'pattern': r'[-+]?[0-9]+.[0-9]+',
        'type': float
    },
    'uuid': {
        'pattern': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
        'type': uuid.UUID
    }
}

class PathNode:
    def __init__(self):
        self.children: Dict[str, PathNode] = None
        self.key: str | None = None
        self.methods: Dict[str, Callable] | None = None

class Path:
    def __init__(self):
        self.root: PathNode = PathNode()

    def insert(self, path: str, func: Callable, methods: List[http.HTTPMethod | str]):
        for method in methods:
            if method != 'WEBSOCKET':
                method = http.HTTPMethod(method)

        node = self.root

        paths = path.split('/')[1:]
        if paths[-1] == '':
            paths = path[:-1]
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

        node.methods = {}
        for method in methods:
            node.methods[method] = func

    def match(self, path: str) -> Tuple[Dict[str, Callable] | None, Dict[str, Any]]:
        paths = path.split('/')[1:]
        if paths[-1] == '' and path != '/':
            paths = paths[:-1]
        return self._match(self.root, paths, {})

    def _match(self, node: PathNode, paths: List[str], kwargs: Dict[str, Any]):
        for i in range(len(paths)):
            if paths[i] not in node.children:
                for key, value in reversed(patterns.items()):
                    if re.fullmatch(value['pattern'], paths[i]) and f'<:{key}>' in node.children:
                        result, kwargs = self._match(node.children[f'<:{key}>'], paths[i + 1:], kwargs)
                        if result:
                            kwargs[node.children[f'<:{key}>'].key] = value['type'](paths[i])
                            return result, kwargs
                return None, {}
            node = node.children[paths[i]]
        if node.methods:
            return node.methods, kwargs
        return None, {}

paths: Path = Path()

class Route:
    def __init__(self, prefix: str = ''):
        self.prefix: str = prefix

    def __call__(self, path: str, methods: List[ http.HTTPMethod | str ]):
        def decorator(func):
            paths.insert(self.prefix + path, func, methods)
        return decorator

    def get(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.GET ])
        return decorator

    def post(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.POST ])
        return decorator

    def delete(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.DELETE ])
        return decorator

    def put(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.PUT ])
        return decorator

    def patch(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.PATCH ])
        return decorator

    def trace(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.TRACE ])
        return decorator

    def options(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.OPTIONS ])
        return decorator

    def head(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.HEAD ])
        return decorator

    def connect(self, path: str):
        def decorator(func):
            paths.insert(self.prefix + path, func, [ http.HTTPMethod.CONNECT ])
        return decorator

    def websocket(self, path: str):
        def decorator(cls):
            instance = cls()
            paths.insert(self.prefix + path, instance, [ 'WEBSOCKET' ])
        return decorator
