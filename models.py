from sqlalchemy import Column, Integer, String
from database import Base

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
    username = Column(String) #, unique=True)
    email = Column(String)
    password = Column(String)

class Reviews(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer)
    user_id = Column(Integer)
    review = Column(String)
    rating = Column(Integer)
