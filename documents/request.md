# **请求**

在`HTTP`和`WEBSOCKET`中，都会有`request`。它在上节《路由》中已经展示了如何获取了。

```python
...
print(request.ip)
key1 = request.args.get('key1')
key2 = request.form.get('key2')
...
```

## **`ip: str`**

请求的来源ip。

## **`path: str`**

被请求的路径，不带`args`。

## **`fullPath: str`**

带`args`的`path`。

## **`scheme: str`**

请求的方式，如`http`、`https`、`ws`、`wss`...

## **`headers: Dict[str, str]`**

请求头。

## **`method: str`**

请求方式，仅在`HTTP`下有。

## **`args: Args`**

请求路径中的`?key=value`。

使用`request.args.get(key: str, default: T = None)`获取值，如果未找到，则返回`None`或自定义默认值。

```python
value = request.args.get('key', None)
```

## **`body`**

请求体，仅在`HTTP`下有。

它有可能是`str`，也有可能是`Dict`，根据请求的格式解析内容。

## **`form: Form`**

表单，仅在`HTTP`下有。

获取值的方式与`args`相同。

```python
value = request.form.get('key', None)
```

## **`sid: str`**

`websocket`连接id，仅在`WEBSOCKET`下有。
