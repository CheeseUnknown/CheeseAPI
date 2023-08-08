import json, traceback, re
from typing import TypeVar, Dict
from urllib.parse import unquote

import CheeseType.network, xmltodict, CheeseLog

from CheeseAPI.file import File

T = TypeVar('T')

class BaseItem:
    def __init__(self):
        self._values: Dict[str, str] = {}

    def get(self, key: str, default: T = None) -> str | File | T:
        if key not in self._values:
            return default
        return self._values[key]

class Request:
    def __init__(self, scope, body: bytes | None = None):
        query_string = scope['query_string'].decode()

        self.ip: CheeseType.network.IPv4 = scope['client'][0]
        self.path: str = unquote(scope['path'])
        self.fullPath: str = self.path + '?' + unquote(query_string) if query_string else self.path
        self.scheme = scope['scheme']

        self.headers: Dict[str, str] = {}

        if scope['type'] in [ 'http', 'https' ]:
            self.method: str = scope['method']
            self.args: Dict[str, str] = {}
            for q in query_string.split('&'):
                q = q.split('=')
                self.args[unquote(q[0])] = unquote(q[1]) if len(q) > 1 else None
            self.body = None
            self.form: Dict[str, str] = {}
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
                            spliter = header[1].split(b'boundary=')[1].split(b';')[0]
                            body = body[2:-4].split(spliter)[1:-1]
                            for s in body:
                                key = re.findall(rb'\bname="(.*?)"', s)[0].decode()
                                value = s.split(b'\r\n\r\n')[1][:-4]
                                filename = re.findall(rb'\bfilename="(.*?)"', s)
                                if len(filename):
                                    self.form[key] = File(filename[0].decode(), value)
                                else:
                                    self.form[key] = value.decode()
                        elif value == 'application/x-www-form-urlencoded':
                            for s in body.decode().split('&'):
                                s = s.split('=')
                                self.form[s[0]] = s[1]
                    except:
                        CheeseLog.danger(f'{self.method} {self.fullPath} cannot parse request.body correctly:\n{traceback.format_exc()}'[:-1], f'\033[36m{self.method} {self.fullPath}\033[0m cannot parse request.body correctly:\n{traceback.format_exc()}'[:-1])
        else:
            for header in scope['headers']:
                key = header[0].decode()
                value = header[1].decode()
                self.headers[key] = value
                if key == 'sec-websocket-key':
                    self.sid: str = value
