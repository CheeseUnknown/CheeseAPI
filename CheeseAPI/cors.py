import http
from typing import Set, Literal

class Cors:
    def __init__(self):
        self.origin: Set[str] | Literal['*'] = '*'
        self.exclude_origin: Set[str] = set()
        self.methods: Set[http.HTTPMethod] = set([ method for method in http.HTTPMethod ])
        self.exclude_methods: Set[http.HTTPMethod] = set()
        self.headers: Set[str] | Literal['*'] = '*'
