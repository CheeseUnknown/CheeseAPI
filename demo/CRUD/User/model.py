import uuid
from enum import Enum

from pydantic import EmailStr, PastDatetime

class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNKNOWN = 'UNKNOWN'

class User:
    def __init__(self, mail: str):
        self.id: uuid.UUID = uuid.uuid4()
        self.mail: EmailStr = mail
        self.gender: Gender = Gender.UNKNOWN
        self.birthDate: PastDatetime | None = None
