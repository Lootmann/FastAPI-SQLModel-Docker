import time
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from api.cruds import auths as auth_api
from api.settings import Settings

credential = Settings()


class TestJWTToken:
    def test_get_username_without_valid_sub_payload(self):
        expire = datetime.utcnow() + timedelta(credential.refresh_token_expire_minutes)
        data = {"exp": expire}
        refresh_token = jwt.encode(
            data, credential.secret_key, algorithm=credential.algorithm
        )

        with pytest.raises(HTTPException):
            auth_api.get_username(refresh_token)
