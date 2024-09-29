import uuid
import sqlalchemy as sa
from datetime import datetime

from .base import Base, ModelInterface, ScopedSession


class SummaryPage(Base, ModelInterface):
    __tablename__ = "summary_pages"

    id = sa.Column(sa.String, primary_key=True)
    title = sa.Column(sa.String)
    url = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime)
    updated_at = sa.Column(sa.DateTime)

    def __init__(self, title: str, url: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.url = url
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"<SummaryPage {self.id} {self.title} {self.url}>"

    @classmethod
    def get_all(cls):
        with ScopedSession() as session:
            return session.query(cls).all()
