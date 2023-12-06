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
        self.headers: Dict[str, str] = {}
        self.args: Dict[str, str] = {}
        try:
            self.fullPath = unquote(self.fullPath)
            for pair in self.fullPath.split('?')[1].split('&'):
                key, value = pair.split('=')
                self.args[unquote(key)] = unquote(value)
        except:
            ...

        if self.scheme in [ 'http', 'https' ]:
            self.method: http.HTTPMethod | None = None
            self.body: str | bytes | None = None
            self.form: Dict[str, str] = {}

    def parseBody(self):
        if 'Content-Type' in self.headers:
            value = self.body
            _value = self.headers.get('Content-Type')
            try:
                if 'application/json' in _value or 'application/javascript' in _value:
                    self.body = json.loads(value)
                elif 'application/xml' in _value:
                    self.body = xmltodict.parse(value)
                elif 'text/plain' in _value or 'text/html' in _value:
                    self.body = value.decode()
                elif 'multipart/form-data' in _value:
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
                elif 'application/x-www-form-urlencoded' in _value:
                    for s in value.decode().split('&'):
                        s = s.split('=')
                        self.form[unquote(s[0])] = unquote(s[1].replace(r'+', r'%20'))
            except:
                logger.danger(f'''An error occurred while accessing {self.method} {self.fullPath}:
Unable to parse body content''', f'''An error occurred while accessing <cyan>{self.method} {self.fullPath}</cyan>:
Unable to parse body content''')
