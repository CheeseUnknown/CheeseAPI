# **Validator**

```python
from CheeseAPI import CheeseAPI, validator, Response

app = CheeseAPI()

class FormValidator(pydantic.BaseModel):
    username: str = pydantic.Field(..., min_length = 3, max_length = 20)
    password: str = pydantic.Field(..., min_length = 6)

@app.route.post('/login')
@validator(form_model = FormValidator)
async def login(*, form_data: FormValidator, **_):
    return Response({
        'username': form_data.username,
        'password': form_data.password
    })
```

## **`def validator(*, json_model: pydantic.BaseModel | None = None, form_model: pydantic.BaseModel | None = None, params_model: pydantic.BaseModel | None = None, headers_model: pydantic.BaseModel | None = None, query_model: pydantic.BaseModel | None = None, hide_body: bool = False) -> Callable`**

对 request 的各个部分进行验证的装饰器

根据不同的 xx_model 参数，返回 **kwargs 中的 xx_data 参数

- **Args**

    - **hide_body**

        是否在验证失败时隐藏错误信息，若为 True 则仅返回 400 状态码，否则返回 400 状态码和错误信息
