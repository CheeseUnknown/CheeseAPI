import uuid

from CheeseAPI import Response, ValidateError
from pydantic import BaseModel, EmailStr, field_validator, PastDatetime

from User import users
from User.model import Gender

class Mail(BaseModel):
    mail: EmailStr

    @field_validator('mail')
    def _mail(cls, value: EmailStr) -> EmailStr:
        for user in users.values():
            if user.mail == value:
                raise ValidateError(Response('该邮箱已被注册', 409))
        return value

class Id(BaseModel):
    id: uuid.UUID

    @field_validator('id')
    def _id(cls, value: uuid.UUID) -> uuid.UUID:
        if value not in users:
            raise ValidateError(Response('没有此id用户', 404))
        return value

class Add(Mail):
    ...

class Delete(Id):
    ...

class SetMail(Id, Mail):
    ...

class SetGender(Id):
    gender: Gender

class SetBirthDate(Id):
    birthDate: PastDatetime
