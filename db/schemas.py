from typing import Union
from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    name: str
    surname: str
    age: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True

