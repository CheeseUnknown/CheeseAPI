import datetime, uuid
from enum import Enum

class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNKNOWN = 'UNKNOWN'

class User:
    def __init__(self, mail: str):
        self.id: uuid.UUID = uuid.uuid4()
        self.mail: str = mail
        self.gender: Gender = Gender.UNKNOWN
        self.birthDate: datetime.datetime | None = None
