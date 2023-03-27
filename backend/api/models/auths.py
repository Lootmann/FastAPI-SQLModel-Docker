from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenUser(SQLModel):
    username: str


class AccessToken(SQLModel):
    access_token: str


class RefeshToken(SQLModel):
    refresh_token: str
