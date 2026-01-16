import threading

import pydantic, requests

import __init__
from CheeseAPI import CheeseAPI, validator, Response

app = CheeseAPI(exclude_modules = ['examples', 'tests'])

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

class PageValidator_Params(pydantic.BaseModel):
    page: int = pydantic.Field(1, ge = 1)

class PageValidator_Query(pydantic.BaseModel):
    size: int = pydantic.Field(10, ge = 1, le = 100)

@app.route.get('/<page:int>')
@validator(query_model = PageValidator_Query, params_model = PageValidator_Params)
async def get_items(*, params_data: PageValidator_Params, query_data: PageValidator_Query, **_):
    return Response({
        'page': params_data.page,
        'size': query_data.size
    })

if __name__ == '__main__':
    threading.Thread(target = app.start, daemon = True).start()

    print(requests.post('http://0.0.0.0:5214/login', data = {
        'username': 'testuser',
        'password': 'securepassword'
    }).json())
    print(requests.get('http://0.0.0.0:5214/1?size=50').json())
