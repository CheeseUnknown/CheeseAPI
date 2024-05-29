import json
from typing import TYPE_CHECKING
from functools import wraps

from pydantic import BaseModel, ValidationError

from CheeseAPI.response import JsonResponse

if TYPE_CHECKING:
    from CheeseAPI.request import Request
    from CheeseAPI.response import BaseResponse

class ValidateError(Exception):
    def __init__(self, response: 'BaseResponse'):
        self.response: 'BaseResponse' = response

def validator(validator: BaseModel):
    '''
    为路由函数添加校验装饰器。

    校验参数以类的校验属性为key，从路径变量、args、form、cookie、headers按顺序尝试匹配，若全部匹配失败，则会默认为None。对于headers中的校验属性，会自动将'_'转换为'-'进行匹配。

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
    '''

    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            request: 'Request' = kwargs['request']

            _kwargs = {}
            for key in validator.model_fields.keys():
                _kwargs[key] = None

                for scope in [ 'path', 'args', 'form', 'cookie', 'headers' ]:
                    try:
                        if scope == 'path':
                            _kwargs[key] = kwargs.get(key)
                        elif scope == 'headers':
                            _kwargs[key] = getattr(request, scope).get(key.replace('_', '-'))
                        else:
                            _kwargs[key] = getattr(request, scope).get(key)

                        if _kwargs.get(key):
                            break
                    except:
                        ...

            try:
                _validator = validator(**_kwargs)
            except ValidationError as e:
                return JsonResponse(json.loads(e.json()), 400)
            except ValidateError as e:
                return e.response

            return await fn(*args, **{
                **kwargs,
                'validator': _validator
            })
        return decorator
    return wrapper
