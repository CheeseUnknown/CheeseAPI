# **详细配置**

app的配置由3个类型组成：

## **系统**

该配置中没有需要修改的内容，它包含了一些系统的配置信息，在项目初始化时自动读取。

```python
from CheeseAPI import app

print(app.system.SYSTEM)
print(app.system.PYTHON_VERSION)
...
```

### **`SYSTEM: CheeseType.System`**

（只读）当前操作设备的系统。

### **`PYTHON_VERSION: str`**

（只读）当前python版本。

### **`CHEESEAPI_VERSION: str`**

（只读）当前CheeseAPI版本。

## **工作空间**

该配置涉及项目结构。

```python
from CheeseAPI import app

app.workspace.STATIC_PATH = '/myStatic/'
app.workspace.MEDIA_PATH = '/myMedia/'
...
```

### **`CHEESEAPI_PATH: str`**

（只读）CheeseAPI的绝对路径。

### **`BASE_PATH: str`**

（只读）当前工作区的绝对路径。

### **`STATIC_PATH: str = '/static/'`**

static文件的相对路径，仅在`app.server.STATIC_PATH`不为`False`的时候生效。

### **`MEDIA_PATH: str = '/media/'`**

media文件的相对路径。

### **`LOG_PATH: str = '/logs/'`**

log文件的相对路径，仅在`app.server.LOG_FILENAME`不为`False`的时候生效。

## **服务器**

该配置涉及服务器的配置。

```python
from CheeseAPI import app

app.server.HOST = '0.0.0.0'
app.server.PORT = 5215
```

### **`HOST: CheeseType.network.Ipv4 = '127.0.0.1'`**

（只读）启动的地址。

### **`WORKERS: CheeseType.NonNegativeInt = 1`**

（只读）worker的数量。

### **`IS_RELOAD: bool = False`**

（只读）热更新。

### **`IS_DEBUG: bool = False`**

DEBUG模式，在该模式下会打印等级为DEBUG的消息。

### **`IS_REQUEST_LOGGED: bool = True`**

该值为`True`，则在控制台会输出等级为HTTP和WEBSOCKET的信息。

如果需要更好的服务器性能，请设置为`False`。

### **`STATIC_PATH: bool | str = False`**

static文件在路由中的位置，默认关闭。

修改为`True`会自动转化为`/`，你可以在路由`/`下访问`app.workspace.STATIC_PATH`中的文件（如果不可浏览的话，则下载）。

static的匹配优先级大于`Route`，请确保文件不会占用已有的路由。

### **`LOG_FILENAME: bool | str = False`**

日志文件，默认为`False`不输出文件。为`True`时会在服务器启动时自动生成格式为`'%Y_%m_%d-%H_%M_%S.log'`的文件，你也可以自定义文件名，消息为追加写入。
