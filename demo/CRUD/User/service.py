import uuid

from pydantic import EmailStr, PastDatetime

from User import users
from User.model import User, Gender

async def add(mail: EmailStr) -> uuid.UUID:
    user = User(mail)
    users[user.id] = user
    return user.id

async def delete(id: uuid.UUID):
    del users[id]

async def setMail(id: uuid.UUID, mail: EmailStr):
    users[id].mail = mail

async def setGender(id: uuid.UUID, gender: Gender):
    users[id].gender = gender

async def setBirthDate(id: uuid.UUID, birthDate: PastDatetime):
    users[id].birthDate = birthDate
