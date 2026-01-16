import threading

import requests

import __init__
from CheeseAPI import CheeseAPI, Response

app = CheeseAPI(exclude_modules = ['examples', 'tests'])

@app.route.get('/')
async def test(**_):
    return Response('Hello, World!')

@app.route.post('/post')
async def test_post(**_):
    return Response(status = 201)

@app.route.put('/put')
async def test_put(**_):
    return Response(status = 403)

@app.route.patch('/patch')
async def test_patch(**_):
    return Response(status = 500)

@app.route.delete('/delete')
async def test_delete(**_):
    return Response(status = 404)

if __name__ == '__main__':
    threading.Thread(target = app.start, daemon = True).start()

    response = requests.get('http://0.0.0.0:5214/')
    print(response.status_code, response.text)

    response = requests.post('http://0.0.0.0:5214/post')
    print(response.status_code, response.text)

    response = requests.put('http://0.0.0.0:5214/put')
    print(response.status_code, response.text)

    response = requests.patch('http://0.0.0.0:5214/patch')
    print(response.status_code, response.text)

    response = requests.delete('http://0.0.0.0:5214/delete')
    print(response.status_code, response.text)
