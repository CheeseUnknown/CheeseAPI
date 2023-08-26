# **Cors**

跨域支持，默认的允许所有跨域请求。

```python
from CheeseAPI import app

app.cors
```

## **`app.cors.origin: Set[str] | Literal['*'] = '*'`**

默认允许所有来源。

```python
from CheeseAPI import app

app.cors.origin = set([ 'http://192.168.1.2' ])
```

## **`app.cors.methods: Set[http.HTTPMethod] = set([ method for method in http.HTTPMethod ])`**

默认允许所有HTTP方法。

```python
from CheeseAPI import app

app.cors.methods = set([ http.HTTPMethod.POST, http.HTTPMethod.PUT, http.HTTPMethod.PATCH, http.HTTPMethod.DELETE, http.HTTPMethod.GET ])
```

## **`app.cors.headers: Set[str] | Literal['*'] = '*'`**

默认允许所有请求头，大小写敏感。

```python
from CheeseAPI import app

app.cors.methods = set([ 'Authorization' ])
```
