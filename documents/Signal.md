# **Signal**

CheeseAPI使用了基于blinker的信号功能。对于项目来说，使用信号开发可以尽可能的解耦代码，但也要保证代码逻辑的清晰。

信号函数会根据注册代码导入顺序按序执行。

## **自定义信号**

### **注册一个信号**

```python
from CheeseAPI import signal

signal.register('myEvent')
signal.register('async_myEvent')
```

### **发送信号**

需要区分接收信号的函数是否支持协程。

```python
from CheeseAPI import singal

def test():
    if signal.receiver('myEvent'):
        signal.send('myEvent')

async def async_test():
    if signal.receiver('async_myEvent'):
        await signal.async_send('async_myEvent')
```

### **接收信号**

```python
from CheeseAPI import signal

@singal.connect('myEvent')
def test(*args, **kwargs):
    ...

@singal.connect('async_myEvent')
async def async_test(*args, **kwargs):
    ...
```

## **内置信号**

CheeseAPI内置了一些信号，它们与公用生命周期插槽的执行顺序相同，使用对应的关键词即可捕获信号，例如：

```python
from CheeseAPI import signal

@singal.connect('server_beforeStartingHandle')
def test(*args, **kwargs):
    ...
```

### **`@signal.connect('server_beforeStartingHandle')`**

在服务器启动之前调用。

### **`@signal.connect('worker_beforeStartingHandle')`**

支持异步函数。

在worker启动之前调用；多worker下会调用多次。

### **`@signal.connect('worker_afterStartingHandle')`**

支持异步函数。

在worker启动之后调用；多worker下会调用多次。

### **`@signal.connect('server_afterStartingHandle')`**

支持异步函数。

在服务器启动之后调用。

### **`@signal.connect('context_beforeFirstRequestHandle')`**

在第一次请求处理前调用；比http_beforeRequestHandle更早。

### **`@signal.connect('http_beforeRequestHandle')`**

支持异步函数。

在请求处理前调用。

### **`@signal.connect('http_afterResponseHandle')`**

支持异步函数。

在响应生成后调用；此时该响应还未发送。

### **`@signal.connect('websocket_beforeConnectionHandle')`**

支持异步函数。

在websocket连接前调用；此时websocket已经构建了连接，仅是在当前websocket的connectHandle调用之前执行。

### **`@signal.connect('websocket_afterDisconnectionHandle')`**

在websocket断开后调用。

### **`@signal.connect('worker_beforeStoppingHandle')`**

支持异步函数。

在worker停止之后调用；多worker下会调用多次。

### **`@signal.connect('server_beforeStoppingHandle')`**

在服务器停止之后调用。
