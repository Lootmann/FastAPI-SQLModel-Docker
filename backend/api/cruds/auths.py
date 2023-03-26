from datetime import datetime, timedelta

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from api.cruds import users as user_api
from api.cruds.custom_exceptions import AuthException
from api.db import get_db
from api.models import auths as auth_model
from api.models import users as user_model
from api.settings import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
credential = Settings()


def hashed_password(plain_text: str) -> str:
    return pwd_context.hash(plain_text)


def verify_password(plain_password: str, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str):
    data = {"sub": username}
    expire = datetime.utcnow() + timedelta(minutes=15)
    data.update({"exp": expire})
    return jwt.encode(data, credential.secret_key, algorithm=credential.algorithm)


def create_refresh_token(username: str):
    data = {"sub": username}
    expire = datetime.utcnow() + timedelta(days=7)
    data.update({"exp": expire})
    return jwt.encode(data, credential.secret_key, algorithm=credential.algorithm)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> user_model.User:
    try:
        payload = jwt.decode(
            token, credential.secret_key, algorithms=[credential.algorithm]
        )
        username: str = payload.get("sub", None)

        if username is None:
            raise AuthException.raise404(detail="User Not Found")

        token = auth_model.TokenUser(username=username)

    except ExpiredSignatureError:
        # TODO: update access_token with refresh_token
        # TODO: token has access and refresh. test both.
        raise AuthException.raise401(detail="Token is Expired")

    except JWTError:
        raise AuthException.raise401(detail="Invalid JWT token")

    user = user_api.find_by_name(db, token.username)

    if user is None:
        raise AuthException.raise401(detail="User Not Found")

    return user
