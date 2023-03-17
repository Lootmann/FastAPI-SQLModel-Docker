from sqlmodel import Session, create_engine

from api.models.users import User
from api.settings import Settings

credential = Settings()
engine = create_engine(credential.db_url, echo=True)


def get_db():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    User.metadata.drop_all(engine)
    User.metadata.create_all(engine)
