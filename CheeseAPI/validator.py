from json import loads
from typing import TYPE_CHECKING
from functools import wraps

from pydantic import BaseModel, ValidationError

from CheeseAPI.response import JsonResponse, Response

if TYPE_CHECKING:
    from CheeseAPI.response import BaseResponse

SCOPES = ('path', 'args', 'form', 'cookie', 'headers')
SCOPES_JSON = ('form', 'args')
JSON_PREFIX = ('{', '[')
JSON_SUFFIX = ('}', ']')

class ValidateError(Exception):
    def __init__(self, response: 'BaseResponse' = Response(status = 400)):
        self.response: 'BaseResponse' = response

def validator(validator: BaseModel):
    '''
    为路由函数添加校验装饰器。

    校验参数以类的校验属性为key，从路径变量、args、form、cookie、headers按顺序尝试匹配，若全部匹配失败，则会默认为None。

    校验通过后，路由函数会收到一个`validator: BaseModel`已校验参数。

    >>> from CheeseAPI import app, validator
    >>> from pydantic import BaseModel, EmailStr, PastDatetime
    >>>
    >>> class User(BaseModel):
    ...    mail: EmailStr
    ...    name: str
    ...    birthDate: PastDatetime
    ...
    >>> @app.route.get('/')
    >>> @validator(Form)
    >>> async def test(*, validator: User, **kwargs):
    ...     ...

    在自定义校验中，可以自定义校验失败后返回的Response：

    >>> from CheeseAPI import ValidateError, Response
    >>> from pydantic import BaseModel, field_validator
    >>>
    >>> class Form(BaseModel):
    ...     value: str
    ... \\
    ...     @field_validator('value')
    ...     def value(cls, value: str) -> str:
    ...         if ...:
    ...             raise ValidateError(Response('My Response', 400))
    '''

    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            _kwargs = {}
            for key in validator.model_fields.keys():
                for scope in SCOPES:
                    if scope == 'path':
                        if key in kwargs:
                            _kwargs[key] = kwargs[key]
                    elif scope == 'headers':
                        _key = key.replace('_', '-')
                        if _key in kwargs['request'].headers:
                            _kwargs[key] = getattr(kwargs['request'], scope)[_key]
                    else:
                        if getattr(kwargs['request'], scope) and key in getattr(kwargs['request'], scope):
                            _kwargs[key] = getattr(kwargs['request'], scope)[key]

                            if scope in SCOPES_JSON and _kwargs[key][0] in JSON_PREFIX and _kwargs[key][-1] in JSON_SUFFIX:
                                try:
                                    _kwargs[key] = loads(_kwargs[key])
                                except:
                                    ...

            try:
                _validator = validator(**_kwargs)
            except ValidationError as e:
                return JsonResponse(loads(e.json()), 400)
            except ValidateError as e:
                return e.response

            return await fn(*args, **{
                **kwargs,
                'validator': _validator
            })
        return decorator
    return wrapper
