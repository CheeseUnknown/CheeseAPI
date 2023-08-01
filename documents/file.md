# **文件**

CheeseAPI提供了方便的文件工具，以便读取文件和保存文件。

## **`class File`**

### **`def __init__(self, path: str)`**

使用相对路径导入项目内的任意文件，在使用它时请确保代码安全。

### **`def __init__(self, name: str, data: bytes)`**

使用名称和字节可假装创建一个文件，它除了没有实体文件外它就是一个文件。

### **`def save(self, path: str | None = None)`**

当`path`为`None`并`self.path`不为`None`时，它会将文件保存到原始路径。

### **`def saveMedia(self, path: str)`**

`path`会加上`self.workspace.MEDIA_PATH`前缀。

## **`class MediaFile(File)`**

### ***`def __init__(self, path: str)`**

`path`会加上`self.workspace.MEDIA_PATH`前缀。
