import re
from typing import List, Literal, Any, Callable, Dict, TYPE_CHECKING
from functools import wraps

from CheeseAPI.response import Response, BaseResponse
from CheeseAPI.request import Request

if TYPE_CHECKING:
    from CheeseAPI.app import App

class ValidateError(Exception):
    def __init__(self, response: BaseResponse = Response('校验错误', 400)):
        '''
        在自定义校验函数中抛出此错误，可结束校验并直接返回响应体。
        '''

        self.response = response

class Bool:
    '''
    将满足小写后等于true或false的字符串转为`bool`。
    '''

    def __new__(cls, value: str) -> bool:
        if not isinstance(value, str):
            raise ValueError('参数类型错误')

        if value.lower() == 'true':
            return True

        if value.lower() == 'false':
            return False

        raise ValueError('格式错误')

class Validator:
    def __init__(self,
        scope: Literal['form', 'headers', 'args', 'path', 'cookie'],
        key: str,
        *,
        required: bool = False,
        default: Any = None,
        type: List[object | Callable] | object | Callable | None = None,
        expected_type: object | None = None,
        pattern: str | None = None,
        min: object | None = None,
        max: object | None = None,
        enum: List[Any] = [],
        fn: Callable | None = None,
        response: Response | None = None
    ):
        '''
        可能的示例：

        ```python
        import datetime

        from CheeseAPI import Validator

        Validator('form', 'date', type = [ float, datetime.datetime.fromtimestamp ], expected_type = datetime.datetime)

        Validator('form', 'gender', enum = [ 'man', 'woman', None ])

        Validator('form', 'idCard', pattern = r'^[1-9]\\d{5}(18|19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\\d|3[0-1])\\d{3}[\\dXx]$', response = Response('身份证格式错误', 400))
        ```

        - Args

            - scope: 域范围。form: request.form；headers: request.headers；args: request.args；path: request.path中的动态路由；cookie: request.cookie。

            - type: 遵循`self.type(value) -> object`的类或函数；支持list按顺序转换类型。

            - expected_type: 期望的数据类型，对type转换后的结果进行二次校验。

            - default: 默认值；该值仍会执行校验流程，而不是直接应用。

            - pattern: 对于`str`类型的数据，使用正则表达式进行验证。

            - enum: 指定某些特定的值。

            - fn: 【更多内容查看完整注释】 自定义校验函数；该函数将在所有预设校验完成后执行。

                该函数结构应为：

                ```python
                from typing import Dict, Any

                async def fn(*args, validatedForm: Dict[str, Any], **kwargs) -> Any:
                    ...
                ```

                参数：

                validatedForm: 之前完成校验的所有数据的字典。

                返回：

                若有返回值，则为该参数的最终值。
        '''

        self._scope: Literal['form', 'headers', 'args', 'path', 'cookie'] = scope
        self.key: str = key
        self._type: List[object | Callable] | object | Callable = type
        self._expected_type: object = type if expected_type is None else expected_type
        self.required: bool = required
        self._default: Any = default
        self._pattern: str | None = pattern
        self.min: object | None = min
        self.max: object | None = max
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError('最小范围不能大于最大范围')
        self._enum: List[Any] = enum
        self._fn: Callable | None = fn
        self._response: Response | None = response

    async def _validate(self, app: 'App', *args, request: Request, validatedForm: Dict[str, object], **kwargs):
        if f'{self.scope}.{self.key}' not in validatedForm:
            if self.scope == 'path':
                validatedForm[f'{self.scope}.{self.key}'] = kwargs[self.key]
            else:
                validatedForm[f'{self.scope}.{self.key}'] = (getattr(request, self.scope) or {}).get(self.key)

        if validatedForm[f'{self.scope}.{self.key}'] is None:
            if self.required:
                raise ValidateError(self.response or Response(app._text.validator_requiredMessage(self.scope, self.key), 400))
            validatedForm[f'{self.scope}.{self.key}'] = self.default
        else:
            if self.type is not None:
                try:
                    if isinstance(self.type, list):
                        for type in self.type:
                            validatedForm[f'{self.scope}.{self.key}'] = type(validatedForm[f'{self.scope}.{self.key}'])
                    else:
                        validatedForm[f'{self.scope}.{self.key}'] = self.type(validatedForm[f'{self.scope}.{self.key}'])
                    if not isinstance(validatedForm[f'{self.scope}.{self.key}'], self.expected_type):
                        raise Exception()
                except:
                    raise ValidateError(self.response or Response(app._text.validator_typeMessage(self.scope, self.key, self.expected_type), 400))

            if self.pattern and not re.match(self.pattern, validatedForm[f'{self.scope}.{self.key}']):
                raise ValidateError(self.response or Response(app._text.validator_patternMessage(self.scope, self.key), 400))

            if self.min and validatedForm[f'{self.scope}.{self.key}'] < self.min:
                raise ValidateError(self.response or Response(app._text.validator_minMessage(self.scope, self.key, self.min), 400))

            if self.max and validatedForm[f'{self.scope}.{self.key}'] > self.max:
                raise ValidateError(self.response or Response(app._text.validator_maxMessage(self.scope, self.key, self.max), 400))

            if self.enum and validatedForm[f'{self.scope}.{self.key}'] not in self.enum:
                raise ValidateError(self.response or Response(app._text.validator_enumMessage(self.scope, self.key, self.enum), 400))

            if self.fn:
                _value = await self.fn(*args, **{
                    'request': request,
                    'validatedForm': validatedForm,
                    **kwargs
                })
                if _value is not None:
                    validatedForm[f'{self.scope}.{self.key}'] = _value

    @property
    def scope(self) -> Literal['form', 'headers', 'args', 'path', 'cookie']:
        '''
        域范围。

        - form: request.form。

        - headers: request.headers。

        - args: request.args。

        - path: request.path中的动态路由。

        - cookie: request.cookie
        '''

        return self._scope

    @scope.setter
    def scope(self, value: Literal['form', 'headers', 'args', 'path', 'cookie']):
        self._scope = value

    @property
    def type(self) -> object | Callable | None:
        '''
        遵循`type(value) -> object`的类或函数；支持list按顺序转换类型。
        '''

        return self._type

    @type.setter
    def type(self, value: object | Callable | None):
        self._type = value

    @property
    def expected_type(self) -> object:
        '''
        期望的数据类型，对type转换后的结果进行二次校验。
        '''

        return self._expected_type

    @expected_type.setter
    def expected_type(self, value: object | None):
        self._expected_type = self.type if value is None else value

    @property
    def default(self) -> Any:
        '''
        默认值；该值仍会执行校验流程，而不是直接应用。
        '''

        return self._default

    @default.setter
    def default(self, value: Any):
        self._default = value

    @property
    def pattern(self) -> str | None:
        '''
        对于`str`类型的数据，使用正则表达式进行验证。
        '''

        return self._pattern

    @pattern.setter
    def pattern(self, value: str | None):
        self._pattern = value

    @property
    def enum(self) -> List[Any]:
        '''
        指定某些特定的值。
        '''

        return self._enum

    @enum.setter
    def enum(self, value: List[Any]):
        self._enum = value

    @property
    def fn(self) -> Callable | None:
        '''
        自定义校验函数；该函数将在所有预设校验完成后执行。

        该函数结构应为：

        ```python
        from typing import Dict, Any

        async def fn(*args, validatedForm: Dict[str, Any], **kwargs) -> Any:
            ...
        ```

        参数：

        validatedForm: 之前完成校验的所有数据的字典。

        返回：

        若有返回值，则为该参数的最终值。
        '''

        return self._fn

    @fn.setter
    def fn(self, value: Callable | None):
        self._fn = value

    @property
    def response(self) -> Response | None:
        '''
        校验失败返回的响应体；若为`None`，则使用系统默认值。
        '''

        return self._response

    @response.setter
    def response(self, value: Response | None):
        self._response = value

def validator(validators: List[Validator]):
    '''
    为路由函数添加校验装饰器。

    校验通过后，路由函数会收到一个`validatedForm: Dict[str, Any]`参数，该参数为转换后的数据字典，key为`f'{validator.scope}.{validator.key}'`；在校验过程中，该参数也会在校验器中传递，其中包含了已经通过校验的数据。

    下面是一个综合示例：

    ```python
    import datetime
    from typing import Any

    from CheeseAPI import app, validator, Validator, Mail

    async def birthDateValidator(*args, validatedForm, **kwargs):
        date = datetime.datetime.now()
        if validatedForm['form.birthDate'] > date:
            raise ValidateError(Response('出生日期异常', 400))

    @app.route.get('/')
    @validator([
        Validator('form', 'name', required = True),
        Validator('form', 'birthDate', type = [ float, datetime.datetime.fromtimestamp ], expected_type = datetime.datetime, fn = birthDateValidator),
        Validator('form', 'gender', enum = [ 'man', 'woman', None ]),
        Validator('form', 'idCard', pattern = r'^[1-9]\\d{5}(18|19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\\d|3[0-1])\\d{3}[\\dXx]$', response = Response('身份证格式错误', 400))
    ])
    async def test(*args, validatedForm: Dict[str, Any], **kwargs):
        ...
    ```

    将一个校验器拆分为两个，可以分布执行校验，以实现优先统一校验某一部分；下面示例将展示如何将birthDate的自定义校验放到所有校验器都完成之后执行：

    ```python
    import datetime
    from typing import Any

    from CheeseAPI import app, validator, Validator, Mail

    async def birthDateValidator(*args, validatedForm, **kwargs):
        date = datetime.datetime.now()
        if validatedForm['form.birthDate'] > date:
            raise ValidateError(Response('出生日期异常', 400))

    @app.route.get('/')
    @validator([
        Validator('form', 'name', required = True),
        Validator('form', 'birthDate', type = [ float, datetime.datetime.fromtimestamp ], expected_type = datetime.datetime),
        Validator('form', 'gender', enum = [ 'man', 'woman', None ]),
        Validator('form', 'idCard', pattern = r'^[1-9]\\d{5}(18|19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\\d|3[0-1])\\d{3}[\\dXx]$', response = Response('身份证格式错误', 400)),
        Validator('form', 'birthDate', fn = birthDateValidator)
    ])
    async def test(*args, validatedForm: Dict[str, Any], **kwargs):
        ...
    ```

    由于在执行自定义校验前已经完成了类型校验，就不再需要重复填写，可直接获取`validatedForm['form.birthDate']`。

    - Args

        - validators: 校验器会按顺序执行。
    '''

    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            from CheeseAPI.app import app

            validatedForm: Dict[str, object] = {}
            for validator in validators:
                try:
                    await validator._validate(app, *args, **{
                        **kwargs,
                        'validatedForm': validatedForm
                    })
                except ValidateError as e:
                    return e.response

            return await fn(*args, **{
                **kwargs,
                'validatedForm': validatedForm
            })
        return decorator
    return wrapper
