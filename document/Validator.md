# **Validator**

为路由函数添加参数校验器，能更方便的处理参数。

## **`def validator(validator: pydantic.BaseModel)`**

为路由函数添加校验装饰器。

校验参数以类的校验属性为key，从路径变量、args、form、cookie、headers按顺序尝试匹配，若全部匹配失败，则会默认为None。

校验通过后，路由函数会收到一个`validator: BaseModel`已校验参数。

```python
from CheeseAPI import app, validator
from pydantic import BaseModel, EmailStr, PastDatetime

class User(BaseModel):
    mail: EmailStr
    name: str
    birthDate: PastDatetime

@app.route.get('/')
@validator(Form)
async def test(*, validator: User, **kwargs):
    ...
```

在自定义校验中，可以自定义校验失败后返回的Response：

```python
from CheeseAPI import ValidateError, Response
from pydantic import BaseModel, field_validator

class Form(BaseModel):
    value: str

    @field_validator('value')
    def value(cls, value: str) -> str:
        if ...:
            raise ValidateError(Response('My Response', 400))

...
```

## **`class ValidateError(Exception)`**

在自定义校验函数中抛出此错误，可结束校验并直接返回响应体。

### **`def __init__(self, response: BaseResponse = Response(status = 400))`**
