import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Request, WebSocket
from fastapi.params import Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jwt import ExpiredSignatureError

from .crud import read_user_by_username
from .model import User
from ...logger import logger

SECRET_KEY = os.getenv("JWTSTRAT", "fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_TIMEDELTA = timedelta(days=7)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE_TIMEDELTA
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request = None, websocket: WebSocket = None,
                           authorization: Optional[str] = Header(None)) -> User | None:
    token = None

    if request is None:
        request = websocket

    if hasattr(request, 'session'):
        token = request.session.get('access_token')
        logger.debug(f"Token from session: {token}")

    if not token and authorization:
        scheme, _, token = authorization.partition(' ')
        if scheme.lower() != 'bearer':
            logger.warning(f"Invalid authorization scheme: {scheme}")
            return None
        logger.debug(f"Token from Authorization header: {token}")

    if not token:
        logger.warning("No token found in session or Authorization header")
        return None
    try:
        logger.debug(f"Attempting to decode token: {token}")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            logger.error(f"Token expired")
            return None
        username: str = payload.get("sub")
        if username is None:
            logger.warning("No username found in token payload")
            return None
        logger.debug(f"Username from token: {username}")
    except JWTError as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None

    user = await read_user_by_username(username=username)
    if user is None:
        logger.warning(f"No user found for username: {username}")
    else:
        logger.debug(f"User found: {user}")
    return user
