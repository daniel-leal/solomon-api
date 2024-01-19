from sqlalchemy import Column, String

from api.solomon.infrastructure.database import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
