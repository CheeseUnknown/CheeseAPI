import os

import __init__
from CheeseAPI import CheeseAPI, Websocket, Response

app = CheeseAPI(exclude_modules = ['examples', 'tests'], sync_server_url = 'redis://0.0.0.0:6379/0', workers = os.cpu_count())

@app.route.websocket('/')
class DefaultWebsocket(Websocket):
    async def on_connect(self):
        print('WebSocket connected!')

    async def on_message(self, message: str | bytes):
        if message == 'close':
            await self.close()
        else:
            await self.send(message)

    async def on_disconnect(self):
        print('WebSocket disconnected!')


@app.route.post('/broadcast')
async def broadcast_message(**_):
    await Websocket.async_send('/', 'hello!')
    return Response()

if __name__ == '__main__':
    app.start()
