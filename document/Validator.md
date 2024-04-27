# **Validator**

为路由函数添加参数校验器，能更方便的处理参数。

## **`def validator(validators: List[Validator])`**

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
    Validator('form', 'idCard', pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])\d{3}[\dXx]$', response = Response('身份证格式错误', 400))
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
    Validator('form', 'idCard', pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])\d{3}[\dXx]$', response = Response('身份证格式错误', 400)),
    Validator('form', 'birthDate', fn = birthDateValidator)
])
async def test(*args, validatedForm: Dict[str, Any], **kwargs):
    ...
```

由于在执行自定义校验前已经完成了类型校验，就不再需要重复填写，可直接获取`validatedForm['form.birthDate']`。

- **参数**

    - **validators**

        校验器会按顺序执行。

## **`class Validator`**

### **`def __init__(self, scope: Literal['form', 'headers', 'args', 'path', 'cookie'], key: str, *, required: bool = False, default: Any = None, type: object | Callable | None = None, expected_type: object | None = None, pattern: str | None = None, min: object | None = None, max: object | None = None, enum: List[Any] = [], fn: Callable | None = None, response: Response | None = None )`**

可能的示例：

```python
import datetime

from CheeseAPI import Validator

Validator('form', 'date', type = [ float, datetime.datetime.fromtimestamp ], expected_type = datetime.datetime)

Validator('form', 'gender', enum = [ 'man', 'woman', None ])

Validator('form', 'idCard', pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2]\d|3[0-1])\d{3}[\dXx]$', response = Response('身份证格式错误', 400))
```

- **参数**

    - **scope**

        域范围。

        - form: request.form。

        - headers: request.headers。

        - args: request.args。

        - path: request.path中的动态路由。

        - cookie: request.cookie。

    - **type**

        遵循`self.type(value) -> object`的类或函数；支持list按顺序转换类型。

    - **expected_type**

        期望的数据类型，对type转换后的结果进行二次校验。

    - **default**

        默认值；该值仍会执行校验流程，而不是直接应用。

    - **pattern**

        对于`str`类型的数据，使用正则表达式进行验证。

    - **enum**

        指定某些特定的值。

    - **fn**

        自定义校验函数；该函数将在所有预设校验完成后执行。

        该函数结构应为：

        ```python
        from typing import Dict, Any

        async def fn(*args, validatedForm: Dict[str, Any], **kwargs) -> Any:
            ...
        ```

        - **参数**

            - **validatedForm**

                之前完成校验的所有数据的字典。

        - **返回**

            若有返回值，则为该参数的最终值。

## **`class Bool`**

将满足小写后等于true或false的字符串转为`bool`。

### **`def __new__(cls, value: str) -> bool`**

## **`class ValidateError(Exception)`**

在自定义校验函数中抛出此错误，可结束校验并直接返回响应体。

### **`def __init__(self, response: BaseResponse = Response('校验错误', 400))`**
