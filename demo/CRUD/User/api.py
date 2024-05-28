from CheeseAPI import Route, validator, Response

from User import service, validator as _validator

route = Route('/User')

@route.post('')
@validator(_validator.Add)
async def add(*, validator: _validator.Add, **_):
    return Response(str(await service.add(validator.mail)), 201)

@route.delete('/<id:uuid>')
@validator(_validator.Delete)
async def delete(*, validator: _validator.Delete, **_):
    await service.delete(validator.id)
    return Response('删除用户成功')

@route.patch('/<id:uuid>/mail')
@validator(_validator.SetMail)
async def setMail(*, validator: _validator.SetMail, **_):
    await service.setMail(validator.id, validator.mail)
    return Response('修改邮箱成功')

@route.patch('/<id:uuid>/gender')
@validator(_validator.SetGender)
async def setGender(*, validator: _validator.SetGender, **_):
    await service.setGender(validator.id, validator.gender)
    return Response('修改性别成功')

@route.patch('/<id:uuid>/birthDate')
@validator(_validator.SetBirthDate)
async def setBirthDate(*, validator: _validator.SetBirthDate, **_):
    await service.setBirthDate(validator.id, validator.birthDate)
    return Response('修改生日成功')
