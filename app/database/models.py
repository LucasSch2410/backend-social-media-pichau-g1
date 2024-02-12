from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, index=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))



class Images(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, nullable=False)
    product_name = Column(String, index=True, nullable=False)
    price = Column(Integer, index=True, nullable=False)
    installment = Column(Integer, index=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    image = Column(String, index=True, nullable=False)
    typeSocial = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

