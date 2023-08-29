# **Module**

该文档为插件开发者准备，如果你只想了解如何管理本地模块，请查看[App](./App.md)。

所有的配置属性都应当存放在项目根目录的`./__init__.py`中。

## **设置依赖项**

如果该模块依赖于其他模块：

```python
CheeseAPI_module_dependencies = [ 'xxx0', 'xxx1' ]
```

在导入该模块前会先按顺序导入依赖模块。

## **设置模块类型**

默认的，模块架构都为单模块，你可以不设置该变量：

```python
CheeseAPI_module_type = 'signle'
```

```
|-- api.py
|-- model.py
|-- service.py
```

CheeseAPI遵循的架构允许外部模块支持多子模块，这样外部模块就可以与项目拥有一样的架构，同时管理过个子模块：

```python
CheeseAPI_module_type = 'multiple'
```

```
|-- subModule0
    |-- api.py
    |-- model.py
    |-- service.py
|-- subModule1
    |-- api.py
    |-- model.py
    |-- service.py
```
