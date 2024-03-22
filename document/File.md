# **File**

一个基础工具，用于读取本地文件以及获取request文件。

## **`class File`**

### **`def __init__(self, filePath: str)`**

通过文件路径进行读取；支持相对路径以及绝对路径。

```python
from CheeseAPI import File

file = File('./media/a.py')
```

### **`def __init__(self, name: str, data: bytes | str)`**

通过二进制数据或字符串创建文件。

```python
from CheeseAPI import File

file = File('test.txt', '这里是CheeseAPI！')
```

### **`def save(self, filePath: str)`**

保存文件；支持相对路径以及绝对路径。
