from datetime import timedelta
from typing import List

from sqlmodel import Session, select

from api.cruds import auths as auth_api
from api.models import users as user_model


def get_all_users(db: Session) -> List[user_model.User]:
    stmt = select(user_model.User)
    return db.exec(stmt).all()


def find_by_id(db: Session, user_id: int) -> user_model.User | None:
    return db.get(user_model.User, user_id)


def find_by_name(db: Session, user_name: str) -> user_model.User | None:
    stmt = select(user_model.User).where(user_model.User.username == user_name)
    return db.exec(stmt).first()


def create_user(db: Session, user_body: user_model.UserCreate) -> user_model.User:
    user = user_model.User(**user_body.dict())
    user.password = auth_api.hashed_password(user_body.password)
    user.refresh_token = auth_api.create_refresh_token(user.username)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session, user: user_model.User, user_body: user_model.UserUpdate
) -> user_model.User:
    user_data = user_body.dict(exclude_unset=True)
    for key, value in user_data.items():
        if key == "password":
            setattr(user, key, auth_api.hashed_password(value))
        else:
            setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: user_model.User) -> None:
    db.delete(user)
    db.commit()
    return
