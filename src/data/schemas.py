from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str


class ChannelResponse(BaseModel):
    id: int
    name: str
    server_id: int


class ServerResponse(BaseModel):
    id: int
    name: str
    owner: UserResponse


class MessageResponse(BaseModel):
    id: int
    content: str
    timestamp: datetime
    author: UserResponse
    answered_id: int | None


class InviteResponse(BaseModel):
    id: int
    link: str
    uses: int
    expire_at: datetime
    creator: UserResponse
    server: ServerResponse
