import http, json, re
from typing import Literal, Dict, List
from urllib.parse import unquote

import xmltodict
from CheeseAPI.file import File

class Request:
    def __init__(self, method: http.HTTPMethod | None, url: str):
        self._fullPath: str = url
        self._path: str = self.fullPath.split('?')[0]
        self._scheme: Literal['http', 'https', 'ws', 'wss'] | None = None
        self._headers: Dict[str, str] = {}
        self._args: Dict[str, str] = {}
        self._method: http.HTTPMethod | Literal['WEBSOCKET'] | None = method
        self._origin: str | None = None
        self._client: str | None = None

        # Http
        self._body: list | dict | str | bytes | None = None
        self._form: Dict[str, str | File] | None = None
        self._cookie: Dict[str, str] | None = None

        # Websocket
        self._subprotocols: List[str] | None = None
        self._subprotocol: str | None = None

        try:
            for pair in self.fullPath.split('?')[1].split('&'):
                key, value = pair.split('=')
                self.args[unquote(key)] = unquote(value)
        except:
            ...

    def _upgrade(self):
        self._scheme = self.scheme.replace('http', 'ws')
        self._method = 'WEBSOCKET'

    def _parseBody(self):
        if 'Content-Type' not in self.headers:
            return

        if 'application/json' in self.headers['Content-Type']:
            self._body = json.loads(self.body)
        elif 'application/xml' in self.headers['Content-Type']:
            self._body = xmltodict.parse(self.body)
        elif 'text/plain' in self.headers['Content-Type'] or 'text/html' in self.headers['Content-Type']:
            self._body = self.body.decode()
        elif 'multipart/form-data' in self.headers['Content-Type']:
            spliter = self.headers['Content-Type'].split('boundary=')[1].split(';')[0]
            self._body = self.body.split(b'--' + spliter.encode())[1:-1]
            self._form = {}
            for t in self.body:
                key = re.findall(rb'name="(.*?)"', t)[0].decode()
                value = t.split(b'\r\n\r\n', 1)[1][:-2]
                filename = re.findall(rb'filename="(.*?)"', t)
                if len(filename):
                    self.form[key] = File(filename[0].decode(), value)
                else:
                    self.form[key] = value.decode()
        elif 'application/x-www-form-urlencoded' in self.headers['Content-Type']:
            self._form = {}
            for t in self.body.decode().split('&'):
                t = t.split('=')
                self.form[unquote(t[0])] = unquote(t[1].replace(r'+', r'%20'))

    @property
    def url(self) -> str | None:
        '''
        【只读】 请求的完整地址，例如：`'http://127.0.0.1:5214/test?key1=value1&key2=value2'`。
        '''

        if not self.scheme or not self.origin:
            return None
        return self.scheme + '://' + self.origin + self.fullPath

    @property
    def fullPath(self) -> str:
        '''
        【只读】 完整路由，例如：`'/test?key1=value1&key2=value2'`。
        '''

        return self._fullPath

    @property
    def path(self) -> str:
        '''
        【只读】 不带参数的路由，例如：`'/test'`。
        '''

        return self._path

    @property
    def scheme(self) -> Literal['http', 'https', 'ws', 'wss'] | None:
        return self._scheme

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def args(self) -> Dict[str, str]:
        return self._args

    @property
    def method(self) -> http.HTTPMethod | Literal['WEBSOCKET'] | None:
        return self._method

    @property
    def origin(self) -> str | None:
        '''
        【只读】 请求的原始url地址。
        '''

        return self._origin

    @property
    def client(self) -> str | None:
        '''
        【只读】 请求的客户端ip。
        '''

        return self._client

    @property
    def body(self) -> list | dict | str | bytes | None:
        return self._body

    @property
    def form(self) -> Dict[str, str | File] | None:
        return self._form

    @property
    def cookie(self) -> Dict[str, str] | None:
        return self._cookie

    @property
    def subprotocols(self) -> List[str] | None:
        '''
        【只读】 Websocket可选的子协议；在http或websocket未提供子协议的时候为`None`。
        '''

        return self._subprotocols

    @property
    def subprotocol(self) -> str | None:
        '''
        【只读】 Websocket选择的子协议；在http、websocket未提供子协议或选择子协议之前的时候为`None`。
        '''

        return self._subprotocol
