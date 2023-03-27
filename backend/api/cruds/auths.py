from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from api.cruds import users as user_api
from api.cruds.custom_exceptions import AuthException
from api.db import get_db
from api.models import users as user_model
from api.settings import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
credential = Settings()


def hashed_password(plain_text: str) -> str:
    return pwd_context.hash(plain_text)


def verify_password(plain_password: str, hashed_password) -> bool:
    return pwd_context.verify(secret=plain_password, hash=hashed_password)


def create_access_token(username: str):
    # NOTE: payload's sub has username, this may cause security issue.
    expire = datetime.utcnow() + timedelta(credential.access_token_expire_minutes)
    data = {"sub": username, "exp": expire}
    return jwt.encode(data, credential.secret_key, algorithm=credential.algorithm)


def create_refresh_token(username: str):
    # NOTE: payload's sub has username, this may cause security issue.
    expire = datetime.utcnow() + timedelta(credential.refresh_token_expire_minutes)
    data = {"sub": username, "exp": expire}
    return jwt.encode(data, credential.secret_key, algorithm=credential.algorithm)


def get_username(token: str) -> str:
    # NOTE: You should ensure that token is valid JWT, and token's sub has username.
    payload = jwt.decode(
        token,
        credential.secret_key,
        algorithms=[credential.algorithm],
    )
    return payload.get("sub")


def check_token(token: str) -> bool:
    """check_token

    1. check jwt has username
    2. check jwt is expired
    3. check jwt is valid

    Args:
        token (str): access_token

    Raises:
        AuthException.raise401: HTTP_401_UNAUTHORIZED,

    Returns:
        bool: True means valid token, False means expired token
    """
    try:
        payload = jwt.decode(
            token,
            credential.secret_key,
            algorithms=[credential.algorithm],
        )
        username: str = payload.get("sub", None)

        if username is None:
            raise AuthException.raise401(detail="Invalid JWT token")

    except ExpiredSignatureError:
        return False

    except JWTError:
        raise AuthException.raise401(detail="Invalid JWT token")

    return True


def get_current_user(
    db: Session = Depends(get_db), access_token: str = Depends(oauth2_scheme)
) -> user_model.User:
    """get_current_user

    Args:
        db (Session): DI
        access_token (str):
            get Bearer token headers: {"Authorization": "Bearer eyJ..."}
            when header has not "Authorization", raise 401 No authorized

    Returns:
        user_model.User: current logged in user
    """
    # check only access_token
    if check_token(access_token):
        username = get_username(access_token)
        user = user_api.find_by_name(db, username)

        if not user:
            raise AuthException.raise401(detail="User Not Found")

        return user

    # NOTE: when this raise happens, try to refresh token
    raise AuthException.raise401(detail="JWT expired")
