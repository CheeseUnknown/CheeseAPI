# **模块**

CheeseAPI允许导入支持的python模块，以及选择性的加载本项目的模块。

## **本地模块**

在默认情况下，项目会自动加载项目根目录下的所有文件夹（隐藏文件夹除外）。

你也可以选择加载某几个个项目：

```python
from CheeseAPI import app

app.localModules = [
    'User',
    'Permission'
]
```

## **外部模块**

如果你的包适配CheeseAPI（也就是能够被CheeseAPI加载），则可以使用该模块的名称导入它：

```python
from CheeseAPI import app

app.modules.add('Module1')
app.modules.add('Module2')
```

如果你想开发一个适配于CheeseAPI的模块，你需要遵循以下几点：

1. 它能够在CheeseAPI中使用。

2. 如果它有模块依赖，则在__init__.py中添加变量：

    ```python
    CheeseAPI_module_dependencies = [
        'Dependency1',
        'Dependency2'
    ]
    ```

    在加载该模块的时候，会自动的加载其依赖模块。
