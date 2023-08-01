# **信号**

信号与装饰器的调用时机相同，只是它会在参数`*args[0]`返回所有的数据。

信号的依赖库是`blinker`。

## **默认信号**

具体含义请查看《装饰器》一节。

```python
from CheeseAPI import signal

@signal.connect('http_beforeRequestHandle')
def a(values):
    print(values)
```

- **server_startingHandle**

- **server_endingHandle**

- **http_response404Handle**

- **http_response405Handle**

- **http_response500Handle**

- **http_beforeRequestHandle**

- **http_afterResponseHandle**

- **websocket_beforeConnectionHandle**

- **websocket_afterDisconnectHandle**

- **websocket_errorHandle**

- **websocket_notFoundHandle**

## **`class Signal`**

```python
from CheeseAPI import signal

signal.register('mySignal')

@signal.connect('mySignal')
def a(values):
    print(values)

@app.route('/', [ 'GET' ])
async def b(request):
    await signal.send_async('mySignal', request)
    ...
```

### **`def register(self, name: str)`**

注册一个信号。

### **`def receiver(self, name: str)`**

获取接收者。

### **`def send(self, name: str, *args, **kwargs)`**

发送信号。

### **`async def send_async(self, name: str, *args, **kwargs)`**

发送一个异步信号。
