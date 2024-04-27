import datetime

from CheeseAPI import ValidateError, Response, Validator

from User import users

async def form_mail_409_fn(*, validatedForm, **_):
    for user in users.values():
        if user.mail == validatedForm['form.mail']:
            raise ValidateError(Response('该邮箱已被注册', 409))

form_mail_409 = Validator('form', 'mail', required = True, pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', fn = form_mail_409_fn)

async def path_id_404_fn(*, validatedForm, **_):
    if validatedForm['path.id'] not in users:
        raise ValidateError(Response('没有此id用户', 404))

path_id_404 = Validator('path', 'id', fn = path_id_404_fn)

async def form_birthDate_400_fn(*, validatedForm, **_):
    date = datetime.datetime.now()
    if validatedForm['form.birthDate'] > date:
        raise ValidateError(Response('来自未来的生日', 400))
