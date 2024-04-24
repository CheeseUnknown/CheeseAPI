import http
from typing import Set, Literal

class Cors:
    def __init__(self):
        self._origin: Set[str] | Literal['*'] = '*'
        self._exclude_origin: Set[str] = set()
        self._methods: Set[http.HTTPMethod] = set([ method for method in http.HTTPMethod ])
        self._exclude_methods: Set[http.HTTPMethod] = set()
        self._headers: Set[str] | Literal['*'] = '*'

    @property
    def origin(self) -> Set[str] | Literal['*']:
        '''
        允许访问的host地址，`'*'`代表允许所有。
        '''

        return self._origin

    @origin.setter
    def origin(self, value: Set[str] | Literal['*']):
        self._origin = value

    @property
    def exclude_origin(self) -> Set[str]:
        '''
        【只读】 不允许访问的host地址；优先级高于`app.cors.origin`。
        '''

        return self._exclude_origin

    @property
    def methods(self) -> Set[http.HTTPMethod]:
        '''
        允许访问的method。
        '''

        return self._methods

    @methods.setter
    def methods(self, value: Set[http.HTTPMethod]):
        self._methods = value

    @property
    def exclude_methods(self) -> Set[http.HTTPMethod]:
        '''
        不允许访问的method；优先级高于`app.cors.methods`。
        '''

        return self._exclude_methods

    @exclude_methods.setter
    def exclude_methods(self, value: Set[http.HTTPMethod]):
        self._exclude_methods = value

    @property
    def headers(self) -> Set[str] | Literal['*']:
        '''
        允许的header keys，`'*'`代表允许所有。
        '''

        return self._headers

    @headers.setter
    def headers(self, value: Set[str] | Literal['*']):
        self._headers = value
