import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Cookie, HTTPException, status

from link_forge.db import DBManager
from link_forge.entities import User
from link_forge.repos import RepoResp, RepoStatus, UserSQLRepo

user_repo = UserSQLRepo(db_manager=DBManager())


JWT_SECRET_KEY: str = os.environ['JWT_SECRET_KEY']
JWT_ALGORITHM: str = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 4
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30


def create_access_token(subject: str) -> str:
    if not isinstance(subject, str):
        raise ValueError('subject must be a string')

    payload: dict[str, Any] = {
        'sub': subject,
        'exp': get_access_token_expires_at(),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    if not isinstance(subject, str):
        raise ValueError('subject must be a string')

    payload: dict[str, Any] = {
        'sub': subject,
        'exp': get_refresh_token_expires_at(),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def decode_refresh_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def get_access_token_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS)


def get_refresh_token_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)


async def require_access_token(
    access_token: str | None = Cookie(default=None),
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token not found',
        )

    try:
        token_payload = decode_access_token(access_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token expired',
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token',
        )

    user_id = token_payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid access token',
        )

    get_user_resp: RepoResp = await user_repo.get_by_id(id=int(user_id))
    if not get_user_resp.ok:
        if get_user_resp.status == RepoStatus.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user'
            )

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    user = get_user_resp.data

    return user


async def require_refresh_token(
    refresh_token: str | None = Cookie(default=None),
) -> User:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token not found',
        )

    try:
        token_payload = decode_refresh_token(refresh_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token expired',
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )

    user_id = token_payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )

    get_user_resp: RepoResp = await user_repo.get_by_id(id=int(user_id))
    if not get_user_resp.ok:
        if get_user_resp.status == RepoStatus.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid user',
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    user = get_user_resp.data

    return user
