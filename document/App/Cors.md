# **Cors**

跨域管理，对非自定义的OPTIONS请求作出响应。

## **`app.cors.origin: Set[str] | Literal['*'] = '*'`**

允许访问的host地址，`'*'`代表允许所有。

## **`app.cors.exclude_origin: Set[str] = set()`**

【只读】 不允许访问的host地址；优先级高于`app.cors.origin`。

## **`app.cors.methods: Set[http.HTTPMethod] = set([ method for method in http.HTTPMethod ])`**

允许访问的method。

## **`app.cors.exclude_methods: Set[http.HTTPMethod] = set()`**

不允许访问的method；优先级高于`app.cors.methods`。

## **`app.cors.headers: Set[str] | Literal['*'] = '*'`**

允许的header keys，`'*'`代表允许所有。
