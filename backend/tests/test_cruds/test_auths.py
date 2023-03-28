from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlmodel import Session

from api.cruds import auths as auth_api
from api.settings import Settings

credential = Settings()


def test_get_username_without_valid_sub_payload():
    expire = datetime.utcnow() + timedelta(credential.refresh_token_expire_minutes)
    data = {"exp": expire}
    refresh_token = jwt.encode(
        data, credential.secret_key, algorithm=credential.algorithm
    )

    with pytest.raises(HTTPException):
        auth_api.get_username(refresh_token)


def test_get_current_user_with_expired_JWT(session: Session, login_fixture):
    # create user
    user, _ = login_fixture

    # create expired JWT
    expire = datetime.utcnow() - timedelta(minutes=1)
    data = {"sub": user.username, "exp": expire}
    access_token = jwt.encode(
        data, credential.secret_key, algorithm=credential.algorithm
    )

    with pytest.raises(Exception) as err:
        auth_api.get_current_user(db=session, access_token=access_token)
    assert str(err.value.detail) == "JWT expired"
