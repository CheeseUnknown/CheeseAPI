import uuid, re, datetime
from typing import List, Literal, Any, Callable, overload, Union
from functools import wraps

class Validator:
    @overload
    def __init__(self,
        scope: Literal['form', 'body', 'headers', 'args', 'path', 'cookie'] | None,
        key: str,
        type: object | Callable,
        *,
        required: bool,
        fn: Callable | None = None,
        message: str | None = None
    ):
        '''
        必要参数校验。

        - Args

            - type: 支持类或函数，最终需要返回一个实例。

            - required: 是否是必要的。

            - fn: 自定义校验函数。

                该函数将在所有预设校验完成后执行，若有返回值，则将代替`message`。

            - message: 校验消息；若为`None`，则使用系统默认值。
        '''

    @overload
    def __init__(self,
        scope: Literal['form', 'body', 'headers', 'args', 'path', 'cookie'] | None,
        key: str,
        type: str = str,
        *,
        default: Any = None,
        pattern: re.Pattern | None = None,
        fn: Callable | None = None,
        message: str | None = None
    ):
        '''
        字符串校验。

        - Args

            - default: 默认值；该值仍会执行校验流程，而不是直接应用。

            - pattern: 正则校验。

            - fn: 自定义校验函数。

                该函数将在所有预设校验完成后执行，若有返回值，则将代替`message`。

            - message: 校验消息；若为`None`，则使用系统默认值。
        '''

    @overload
    def __init__(self,
        scope: Literal['form', 'body', 'headers', 'args', 'path', 'cookie'] | None,
        key: str,
        type: uuid.UUID = uuid.UUID,
        *,
        default: Any = None,
        fn: Callable | None = None,
        message: str | None = None
    ):
        '''
        uuid校验。

        - Args

            - default: 默认值；该值仍会执行校验流程，而不是直接应用。

            - fn: 自定义校验函数。

                该函数将在所有预设校验完成后执行，若有返回值，则将代替`message`。

            - message: 校验消息；若为`None`，则使用系统默认值。
        '''

    @overload
    def __init__(self,
        scope: Literal['form', 'body', 'headers', 'args', 'path', 'cookie'] | None,
        key: str,
        type: object | Callable,
        *,
        default: Any = None,
        min: object | None = None,
        max: object | None = None,
        fn: Callable | None = None,
        message: str | None = None
    ):
        '''
        uuid校验。

        - Args

            - type: 支持类或函数，最终需要返回一个实例。

                特殊的，返回实例能够进行大小判断。

            - default: 默认值；该值仍会执行校验流程，而不是直接应用。

            - min: 最小值限制。

            - max: 最大值限制。

            - fn: 自定义校验函数。

                该函数将在所有预设校验完成后执行，若有返回值，则将代替`message`。

            - message: 校验消息；若为`None`，则使用系统默认值。
        '''

    def __init__(self,
        scope: Literal['form', 'body', 'headers', 'args', 'path', 'cookie'] | None,
        key: str,
        type: object | Callable,
        *,
        required: bool = False,
        default: Any = None,
        pattern: re.Pattern | None = None,
        min: object | None = None,
        max: object | None = None,
        fn: Callable | None = None,
        message: str | None = None
    ):
        ...

def validator(validators: List[Validator]):
    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            for validator in validators:
                ...

            return await fn(*args, **kwargs)
        return decorator
    return wrapper
