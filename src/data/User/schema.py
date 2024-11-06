from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str

