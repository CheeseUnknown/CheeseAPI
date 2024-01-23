# **File**

## **`File(arg0: str, arg1: bytes | None = None)`**

提供路径，快速生成文件类：

```python
from CheeseAPI import File

file = File('./a.txt')
```

或提供文件名和二进制数据：

```python
from CheeseAPI import File

file = File('a.txt', r'123')
```

`request.form`中传输的文件，提供的也是该类。
