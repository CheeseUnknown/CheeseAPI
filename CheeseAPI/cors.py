import http
from typing import Set, Literal

class Cors:
    def __init__(self):
        self.origin: Set[str] | Literal['*'] = '*'
        self.methods: Set[http.HTTPMethod] = set([ method for method in http.HTTPMethod ])
        self.headers: Set[str] | Literal['*'] = '*'
