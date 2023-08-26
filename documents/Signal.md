# **Signal**

CheeseAPI使用了基于blinker的信号功能。对于项目来说，使用信号开发可以尽可能的解耦代码，但也要保证代码逻辑的清晰。

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
def async_test(*args, **kwargs):
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

更多请查看[生命周期](./生命周期.md)。
