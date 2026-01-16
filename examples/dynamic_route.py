'''
CheeseAPI 内置四种动态路由类型：
- str: 匹配字符串
- int: 匹配 int
- float: 匹配 float
- uuid: 匹配 UUID

也可以通过 route_patterns 参数自定义动态路由类型，例如下面的 email 类型
'''

import re, threading
from typing import TYPE_CHECKING

import requests

import __init__
from CheeseAPI import CheeseAPI, Response

if TYPE_CHECKING:
    from CheeseAPI.request import Request

app = CheeseAPI(route_patterns = [
    {
        'key': 'email',
        'pattern': re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'),
        'type': str,
        'weight': 10
    }
], exclude_modules = ['examples', 'tests'])

@app.route.get('/<id:uuid>')
async def test(*, request: 'Request', **_):
    print('uuid', request.params['id'])
    return Response('Hello, World!')

@app.route.get('/<key:str>')
async def test(*, request: 'Request', **_):
    print('str', request.params['key'])
    return Response('Hello, World!')

@app.route.get('/<page:int>')
async def test(*, request: 'Request', **_):
    print('int', request.params['page'])
    return Response('Hello, World!')

@app.route.get('/<number:float>')
async def test(*, request: 'Request', **_):
    print('float', request.params['number'])
    return Response('Hello, World!')

@app.route.get('/<email:email>')
async def test(*, request: 'Request', **_):
    print('email', request.params['email'])
    return Response('Hello, World!')

if __name__ == '__main__':
    threading.Thread(target = app.start, daemon = True).start()

    requests.get('http://0.0.0.0:5214/550e8400-e29b-41d4-a716-446655440000')
    requests.get('http://0.0.0.0:5214/abcdefg')
    requests.get('http://0.0.0.0:5214/123')
    requests.get('http://0.0.0.0:5214/123.643')
    requests.get('http://0.0.0.0:5214/test@gmail.com')
