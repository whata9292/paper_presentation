from typing import Any, Callable
from functools import wraps
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
import uuid
from datetime import datetime

engine = create_engine(
    "postgresql://{user}:{password}@{host}/{dbname}".format(
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        dbname=os.environ.get("DB_NAME"),
    )
)

Base = declarative_base()

ScopedSession = scoped_session(
    sessionmaker(
        bind=engine,
        expire_on_commit=False,
    ),
)


class ModelInterface:
    @classmethod
    def find(cls, idn):
        db = ScopedSession()
        return db.query(cls).filter(cls.id == idn).first()

    @classmethod
    def create(cls, **kwargs):
        return cls(id=str(uuid.uuid4()), **kwargs)

    def update(self):
        self.updated_at = datetime.now()


def entrypoint(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def _entry_point(*args: Any, **keywords: Any) -> Any:
        session: Session = ScopedSession()
        try:
            result = func(*args, **keywords)
        except Exception as e:
            session.rollback()
            raise e
        else:
            session.commit()
        finally:
            ScopedSession.remove()
        return result

    return _entry_point
