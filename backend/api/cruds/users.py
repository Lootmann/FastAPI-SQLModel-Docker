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


def create_user(db: Session, user_body: user_model.UserCreate) -> user_model.User:
    user = user_model.User(**user_body.dict())
    user.password = auth_api.hashed_password(user_body.password)

    data = {"sub": user.name}
    user.refresh_token = auth_api.create_refresh_token(data)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
