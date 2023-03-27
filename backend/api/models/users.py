from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, min_length=5, max_length=100)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    # TODO: One of the implementation will not have refresh_token
    refresh_token: str


class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=100)


class UserRead(UserBase):
    id: int


class UserUpdate(UserBase):
    password: str
