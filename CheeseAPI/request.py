import http, json, re
from typing import Dict, Literal
from urllib.parse import unquote

import xmltodict
from CheeseLog import logger

from CheeseAPI.file import File

class Request:
    def __init__(self, url: str):
        self.url: str = url
        self.fullPath: str = '/' + '/'.join(self.url.split('/')[3:])
        self.path: str = self.fullPath.split('?')[0]
        self.scheme: Literal[ 'http', 'https', 'ws', 'wws' ] = self.url.split('://')[0]
        self.header: Dict[str, str] = {}
        self.query: Dict[str, str] = {}
        try:
            for pair in self.fullPath.split('?')[1].split('&'):
                key, value = pair.split('=')
                self.query[key] = value
        except:
            ...

        if self.scheme in [ 'http', 'https' ]:
            self.method: http.HTTPMethod | None = None
            self._body: str | bytes | None = None
            self.form: Dict[str, str] = {}

    @property
    def body(self) -> str | bytes | None:
        if self.scheme in [ 'http', 'https' ]:
            return self._body

    @body.setter
    def body(self, value: bytes):
        if 'Content-Type' in self.header:
            _value = self.header.get('Content-Type')
            try:
                if _value in [ 'application/json', 'application/javascript' ]:
                    self._body = json.loads(value)
                elif _value == 'application/xml':
                    self._body = xmltodict.parse(value)
                elif _value in [ 'text/plain', 'text/html' ]:
                    self._body = value.decode()
                elif _value.startswith('multipart/form-data;'):
                    spliter = _value.split('boundary=')[1].split(';')[0]
                    body = value.split(b'--' + spliter.encode())[1:-1]
                    for s in body:
                        key = re.findall(rb'name="(.*?)"', s)[0].decode()
                        value = s.split(b'\r\n\r\n')[1][:-2]
                        filename = re.findall(rb'filename="(.*?)"', s)
                        if len(filename):
                            self.form[key] = File(filename[0].decode(), value)
                        else:
                            self.form[key] = value.decode()
                elif _value == 'application/x-www-form-urlencoded':
                    for s in value.decode().split('&'):
                        s = s.split('=')
                        self.form[unquote(s[0])] = unquote(s[1])
            except:
                logger.danger(f'''An error occurred while accessing {self.method} {self.fullPath}:
Unable to parse body content''', f'''An error occurred while accessing <cyan>{self.method} {self.fullPath}</cyan>:
Unable to parse body content''')
