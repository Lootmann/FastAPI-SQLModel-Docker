from typing import List

from sqlmodel import Session, select

from api.models import users as user_model


def get_all_users(db: Session) -> List[user_model.User]:
    stmt = select(user_model.User)
    return db.exec(stmt).all()


def create_user(db: Session, user_body: user_model.UserCreate) -> user_model.User:
    user = user_model.User(**user_body.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
