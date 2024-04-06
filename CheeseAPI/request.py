import http, json, re
from typing import Literal, Dict, List
from urllib.parse import unquote

import xmltodict
from CheeseAPI.file import File

class Request:
    def __init__(self, method: http.HTTPMethod, url: str):
        self.fullPath: str = url
        self.path: str = self.fullPath.split('?')[0]
        self.scheme: Literal['http', 'https', 'ws', 'wss'] | None = None
        self.headers: Dict[str, str] = {}
        self.args: Dict[str, str] = {}
        self.method: http.HTTPMethod | Literal['WEBSOCKET'] = method
        self.origin: str | None = None
        self.client: str | None = None

        # Http
        self.body: list | dict | str | bytes | None = None
        self.form: Dict[str, str | File] | None = None
        self.cookie: Dict[str, str] | None = None

        # Websocket
        self.subprotocols: List[str] | None = None
        self.subprotocol: str | None = None

        try:
            for pair in self.fullPath.split('?')[1].split('&'):
                key, value = pair.split('=')
                self.args[unquote(key)] = unquote(value)
        except:
            ...

    def _upgrade(self):
        self.scheme = self.scheme.replace('http', 'ws')
        self.method = 'WEBSOCKET'

    def _parseBody(self):
        if 'Content-Type' not in self.headers:
            return

        if 'application/json' in self.headers['Content-Type']:
            self.body = json.loads(self.body)
        elif 'application/xml' in self.headers['Content-Type']:
            self.body = xmltodict.parse(self.body)
        elif 'text/plain' in self.headers['Content-Type'] or 'text/html' in self.headers['Content-Type']:
            self.body = self.body.decode()
        elif 'multipart/form-data' in self.headers['Content-Type']:
            spliter = self.headers['Content-Type'].split('boundary=')[1].split(';')[0]
            self.body = self.body.split(b'--' + spliter.encode())[1:-1]
            self.form = {}
            for t in self.body:
                key = re.findall(rb'name="(.*?)"', t)[0].decode()
                value = t.split(b'\r\n\r\n', 1)[1][:-2]
                filename = re.findall(rb'filename="(.*?)"', t)
                if len(filename):
                    self.form[key] = File(filename[0].decode(), value)
                else:
                    self.form[key] = value.decode()
        elif 'application/x-www-form-urlencoded' in self.headers['Content-Type']:
            self.form = {}
            for t in self.body.decode().split('&'):
                t = t.split('=')
                self.form[unquote(t[0])] = unquote(t[1].replace(r'+', r'%20'))

    @property
    def url(self) -> str | None:
        if not self.scheme or not self.origin:
            return None
        return self.scheme + '://' + self.origin + self.fullPath
