# **RouteBus**

路由总线管理app的路由，对请求进行404以及405的初步判断。

## **`app.routeBus.patterns: List[Dict[str, Any]]`**

【只读】 可匹配的动态路由参数，默认值为：

```python
import uuid

app.routeBus.patterns = [
    {
        'key': 'uuid',
        'pattern': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
        'type': uuid.UUID,
        'weight': 10
    },
    {
        'key': 'float',
        'pattern': r'[-+]?[0-9]+\.[0-9]+',
        'type': float,
        'weight': 10
    },
    {
        'key': 'int',
        'pattern': r'[-+]?[0-9]+',
        'type': int,
        'weight': 10
    },
    {
        'key': 'str',
        'pattern': r'.+',
        'type': str,
        'weight': 0
    }
]
```

若想要添加动态路由，请使用`app.routeBus.addPattern(key: str, pattern: str, type: object, weight: int)`。

- **`key: str`**

    在动态路由中的key；uuid可替换为其他类型的参数key。

    ```python
    import uuid

    from CheeseAPI import app

    @app.route.get('/<id:uuid>')
    async def test(id: uuid.UUID, **kwargs):
        ...
    ```

- **`pattern: str`**

    使用正则匹配动态路由的字符串。

- **`type: object`**

    若匹配成功，则会将字符串转为该类；请确保该类可以使用`Xxx(value: str)`进行转换，或是一个返回值为该类的函数。

- **`weight: int`**

    匹配优先级的权重；更高的权重意味着优先级更高的匹配，若匹配成功则不会继续匹配。

## **`app.routeBus.addPattern(key: str, pattern: str, type: object, weight: int)`**

新增动态路由匹配条件；具体参数与`app.routeBus.patterns`所述相同。
