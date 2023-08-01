import re, uuid
from typing import Self, Callable, Dict, List, Tuple, Any

PATTERNS: Dict[str, re.Pattern] = {
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
        'pattern': r'r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"',
        'type': uuid.UUID
    }
}

_PATHS: dict = {}

class _MatchPathNode:
    def __init__(self):
        self.children: dict = {}
        self.key: str | None = None
        self.isEnd: bool = False

class _MatchPath:
    def __init__(self):
        self.root: _MatchPathNode = _MatchPathNode()

    def insert(self, path: str, func: Callable, methods: List[str]):
        node = self.root
        for part in path.split('/')[1:]:
            if re.match(r'<\w+:\w+>', part):
                part = part[1:-1].split(':')
                _part = f'<:{part[1]}>'
                if _part not in node.children:
                    node.children[_part] = _MatchPathNode()
                node.children[_part].key = part[0]
                part = _part
            else:
                if part not in node.children:
                    node.children[part] = _MatchPathNode()
            node = node.children[part]
        node.isEnd = True

        for method in methods:
            node.children[method] = func

    def match(self, path: str) -> Tuple[Dict[str, Callable], Dict[str, Any]]:
        kwargs = {}
        node = self.root
        for part in path.split('/')[1:]:
            if part not in node.children:
                flag = False
                for key, value in reversed(PATTERNS.items()):
                    if re.fullmatch(value['pattern'], part) and f'<:{key}>' in node.children:
                        kwargs[node.children[f'<:{key}>'].key] = value['type'](part)
                        part = f'<:{key}>'
                        flag = True
                        break
                if not flag:
                    return None, {}
            node = node.children[part]
        if node.isEnd:
            return node.children, kwargs
        else:
            return None, {}

_MATCH_PATH: _MatchPath = _MatchPath()

class Route:
    def __init__(self, prefix: str = '', parent: Self | None = None):
        self.parent: Route | None = parent
        if self.parent is not None:
            self.parent.routers.append(self)
            prefix = self.parent.prefix + prefix
        self.prefix: str = prefix
        self.routers: List[Route] = []
        self.paths: Dict[str, Dict[str, Callable]] = {}

    def __call__(self, path: str, methods: List[str]):
        def decorator(func):
            self.default(path, methods, func)
        return decorator

    def default(self, path: str, methods: List[str], func: Callable):
        _path = self.prefix + path
        if _path not in _PATHS:
            _PATHS[_path] = {}
        if _path not in self.paths:
            self.paths[_path] = {}

        if not isinstance(_PATHS[_path], dict):
            _PATHS[_path] = {}
        for method in methods:
            _PATHS[_path][method] = func
            self.paths[_path][method] = func

        _MATCH_PATH.insert(_path, func, methods)

    def get(self, path: str):
        def decorator(func):
            self.default(path, [ 'GET' ], func)
        return decorator

    def post(self, path: str):
        def decorator(func):
            self.default(path, [ 'POST' ], func)
        return decorator

    def delete(self, path: str):
        def decorator(func):
            self.default(path, [ 'DELETE' ], func)
        return decorator

    def patch(self, path: str):
        def decorator(func):
            self.default(path, [ 'PATCH' ], func)
        return decorator

    def put(self, path: str):
        def decorator(func):
            self.default(path, [ 'PUT' ], func)
        return decorator

    def websocket(self, path: str):
        def decorator(func):
            self.default(path, [ 'WEBSOCKET' ], func)
        return decorator

def matchPath(path: str) -> Tuple[Dict[str, Callable], Dict[str, Any]]:
    if path in _PATHS:
        return _PATHS[path], {}

    return _MATCH_PATH.match(path)
