import datetime

from CheeseAPI import Route, Validator, validator, Response

from User import service, validator as _validator
from User.model import Gender

route = Route('/User')

@route.post('')
@validator([
    _validator.form_mail_409
])
async def add(*, validatedForm, **_):
    return Response(str(await service.add(validatedForm['form.mail'])), 201)

@route.delete('/<id:uuid>')
@validator([
    _validator.path_id_404
])
async def delete(*, validatedForm, **_):
    await service.delete(validatedForm['path.id'])
    return Response('删除用户成功')

@route.patch('/<id:uuid>/mail')
@validator([
    _validator.path_id_404,
    _validator.form_mail_409
])
async def setMail(*, validatedForm, **_):
    await service.setMail(validatedForm['path.id'], validatedForm['form.mail'])
    return Response('修改邮箱成功')

@route.patch('/<id:uuid>/gender')
@validator([
    _validator.path_id_404,
    Validator('form', 'gender', required = True, type = Gender)
])
async def setGender(*, validatedForm, **_):
    await service.setGender(validatedForm['path.id'], validatedForm['form.gender'])
    return Response('修改性别成功')

@route.patch('/<id:uuid>/birthDate')
@validator([
    _validator.path_id_404,
    Validator('form', 'birthDate', required = True, type = [ float, datetime.datetime.fromtimestamp ], expected_type = datetime.datetime, fn = _validator.form_birthDate_400_fn)
])
async def setBirthDate(*, validatedForm, **_):
    await service.setBirthDate(validatedForm['path.id'], validatedForm['form.birthDate'])
    return Response('修改生日成功')
