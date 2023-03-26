from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from api.cruds import auths as auth_api
from api.cruds import users as user_api
from api.cruds.custom_exceptions import AuthException
from api.db import get_db
from api.models import auths as auth_model

router = APIRouter(tags=["auth"], prefix="/auth")


@router.get(
    "/refresh",
    response_model=auth_model.Token,
    status_code=status.HTTP_200_OK,
)
def refresh_access_token(
    *,
    db: Session = Depends(get_db),
    token: auth_model.Token,
):
    """
    Refresh access_token endpoint.
    This will generate a new access token from the refresh token.
    """
    # TODO: check refresh token, when refresh is not expired, re-create access_token
    if auth_api.check_token(token.refresh_token):
        username = auth_api.get_username(token.refresh_token)

        user = user_api.find_by_name(db, username)
        if not user:
            raise AuthException.raise404(detail="User Not Found")

        new_token = token
        new_token.access_token = auth_api.create_access_token(username)
        return new_token

    # TODO: when refresh token is expired, API to /auth/token, create refresh token again
    raise AuthException.raise401(detail="Relogin")


@router.post(
    "/token",
    response_model=auth_model.Token,
    status_code=status.HTTP_201_CREATED,
)
def create_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    found = user_api.find_by_name(db, form_data.username)

    if not found:
        raise AuthException.raise404(detail="User Not Found")

    if not auth_api.verify_password(form_data.password, found.password):
        raise AuthException.raise401(detail="username is password is invalid")

    token = auth_model.Token(
        access_token=auth_api.create_access_token(found.username),
        refresh_token=auth_api.create_refresh_token(found.username),
        token_type="bearer",
    )
    return token
