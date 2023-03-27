from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from api.cruds import auths as auth_api
from api.cruds import users as user_api
from api.db import get_db
from api.models import users as user_model

router = APIRouter(tags=["users"], prefix="/users")


@router.get(
    "",
    response_model=List[user_model.UserRead],
    status_code=status.HTTP_200_OK,
)
def get_all_users(
    *,
    db: Session = Depends(get_db),
    _=Depends(auth_api.get_current_user),
):
    return user_api.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=user_model.UserRead,
    status_code=status.HTTP_200_OK,
)
def get_user_by_id(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    _=Depends(auth_api.get_current_user),
):
    return user_api.find_by_id(db, user_id)


@router.post(
    "",
    response_model=user_model.UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    *,
    db: Session = Depends(get_db),
    user: user_model.UserCreate,
):
    return user_api.create_user(db, user)


@router.patch(
    "",
    response_model=user_model.UserRead,
    status_code=status.HTTP_200_OK,
)
def update_user(
    *,
    db: Session = Depends(get_db),
    user: user_model.UserUpdate,
    current_user=Depends(auth_api.get_current_user),
):
    return user_api.update_user(db, current_user, user)


@router.delete("", response_model=None, status_code=status.HTTP_200_OK)
def delete_user(
    *,
    db: Session = Depends(get_db),
    current_user=Depends(auth_api.get_current_user),
):
    return user_api.delete_user(db, current_user)
