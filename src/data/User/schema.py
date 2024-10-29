from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    session: str


class User(BaseModel):
    id: int
    username: str
    email: str
    session: str
