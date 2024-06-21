from sqlalchemy import Column, Integer, String, ForeignKey, Table
import sqlalchemy.types as types
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base
import json


# ---------------- Database Table Models ***Edit as needed*** ---------------- #
class Books(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    rating = Column(Integer)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)  # , unique=True)
    email = Column(String)
    password = Column(String)


class Reviews(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer)
    user_id = Column(Integer)
    review = Column(String)
    rating = Column(Integer)


class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String)


image_tag_table = Table(
    "link_tags",
    Base.metadata,
    Column("image_id", Integer, ForeignKey("images.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)


class JsonWrapper(types.TypeDecorator):
    impl = types.Unicode
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

class Images(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    user_id = Column(Integer)
    description = Column(String)
    rectangles = Column(JsonWrapper)
    tags = relationship(Tags, secondary=image_tag_table)
