import time

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from api.cruds import auths as auth_api
from api.cruds import users as user_api
from api.cruds.custom_exceptions import AuthException
from api.db import get_db
from api.models import auths as auth_model

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post(
    "/refresh",
    response_model=auth_model.AccessToken,
    status_code=status.HTTP_200_OK,
)
def refresh_access_token(
    *,
    db: Session = Depends(get_db),
    token: auth_model.RefeshToken,
):
    """
    Refresh access_token endpoint.
    This will generate a new access token from the refresh token.
    """
    # NOTE: check refresh token, when refresh is not expired, re-create access_token
    if auth_api.check_token(token.refresh_token):

        # NOTE: check_token already checked token has username
        username = auth_api.get_username(token.refresh_token)

        user = user_api.find_by_name(db, username)
        if not user:
            raise AuthException.raise404(detail="User Not Found")

        # NOTE: refresh access_token
        token = auth_model.AccessToken(
            access_token=auth_api.create_access_token(username)
        )
        return token

    # NOTE: when refresh token is expired, API to /auth/token, create refresh token again
    raise AuthException.raise401(detail="You need Login D:")


@router.post(
    "/token",
    response_model=auth_model.Token,
    status_code=status.HTTP_201_CREATED,
)
def create_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2PasswordRequestForm dependencies "username" and "password"
    when your post request does NOT have these body params,
    raise "HTTP_422 Unprocessable Entity"
    """
    if len(form_data.username) < 5:
        raise AuthException.raise401(detail="Username must be at least 5 chars long")

    if len(form_data.password) < 5:
        raise AuthException.raise401(detail="Password must be at least 5 chars long")

    found = user_api.find_by_name(db, form_data.username)

    if not found:
        time.sleep(0.5)
        raise AuthException.raise401(detail="username of password is invalid")

    if not auth_api.verify_password(form_data.password, found.password):
        raise AuthException.raise401(detail="username or password is invalid")

    token = auth_model.Token(
        access_token=auth_api.create_access_token(found.username),
        refresh_token=auth_api.create_refresh_token(found.username),
        token_type="bearer",
    )

    # update refresh token
    found.refresh_token = token.refresh_token
    db.add(found)
    db.commit()
    db.refresh(found)

    return token
