# **File**

一个简单的文件类，用于对文件的处理

```python
from CheeseAPI import File
```

## **`def __init__(self, path: str, *, data_in_file: bool = True)`**

- **Args**

    - **data_in_file**

        否将数据保存在文件中，若否则读取文件内容到内存

## **`def __init__(self, name: str, data: bytes)`**

## **`self.path: str | None`**

## **`self.data_in_file: bool`**

是否将数据保存在文件中，若否则读取文件内容到内存

## **`self.data: bytes`**

## **`self.name: str`**

## **`def save(self, path: str, update_path: bool = False, data_in_file: bool = False)`**

- **Args**

    - **update_path**

        是否更新文件路径为保存后的路径

    - **data_in_file**

        是否将数据保存在文件中，若否则读取文件内容到内存