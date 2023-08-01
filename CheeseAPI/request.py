import json, traceback, re
from typing import TypeVar, overload, Dict

import CheeseType.network, xmltodict, CheeseLog

from .file import File

T = TypeVar('T')

class BaseItem:
    def __init__(self):
        self._values: Dict[str, str] = {}

    def get(self, key: str, default: T = None) -> str | File | T:
        if key not in self._values:
            return default
        return self._values[key]

class Args(BaseItem):
    def __init__(self, query: str):
        super().__init__()

        for q in query.split('&'):
            q = q.split('=')
            self._values[q[0]] = q[1] if len(q) > 1 else None

class Form(BaseItem):
    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, body: str):
        ...

    @overload
    def __init__(self, body: bytes, spliter: bytes):
        ...

    def __init__(self, body: str | bytes | None = None, spliter: bytes | None = None):
        super().__init__()

        if body and not spliter:
            for s in body.split('&'):
                s = s.split('=')
                self._values[s[0]] = s[1]

        elif body and spliter:
            body = body[2:-4].split(spliter)[1:-1]
            for s in body:
                key = re.findall(rb'\bname="(.*?)"', s)[0].decode()
                value = s.split(b'\r\n\r\n')[1][:-4]
                filename = re.findall(rb'\bfilename="(.*?)"', s)
                if len(filename):
                    self._values[key] = File(filename[0].decode(), value)
                else:
                    self._values[key] = value.decode()

class Request:
    def __init__(self, scope, body: bytes | None = None):
        query_string = scope['query_string'].decode()

        self.ip: CheeseType.network.IPv4 = scope['client'][0]
        self.path: str = scope['path']
        self.fullPath: str = self.path + '?' + query_string if query_string else self.path
        self.scheme = scope['scheme']

        self.headers: Dict[str, str] = {}

        if scope['type'] in [ 'http', 'https' ]:
            self.method: str = scope['method']
            self.args = Args(query_string)
            self.body = None
            self.form: Form = Form()
            for header in scope['headers']:
                key = header[0].decode()
                value = header[1].decode()
                self.headers[key] = value
                if key == 'content-type':
                    try:
                        if value in [ 'application/json', 'application/javascript' ]:
                            self.body = json.loads(body)
                        elif value == 'application/xml':
                            self.body = xmltodict.parse(body)
                        elif value in [ 'text/plain', 'text/html' ]:
                            self.body = body.decode()
                        elif value.startswith('multipart/form-data;'):
                            self.form = Form(body, header[1].split(b'boundary=')[1].split(b';')[0])
                        elif value == 'application/x-www-form-urlencoded':
                            self.form = Form(body.decode())
                    except:
                        CheeseLog.danger(f'{self.method} {self.fullPath} cannot parse request.body correctly:\n{traceback.format_exc()}'[:-1], f'\033[36m{self.method} {self.fullPath}\033[0m cannot parse request.body correctly:\n{traceback.format_exc()}'[:-1])
        else:
            for header in scope['headers']:
                key = header[0].decode()
                value = header[1].decode()
                self.headers[key] = value
                if key == 'sec-websocket-key':
                    self.sid: str = value
