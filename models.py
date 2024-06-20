from sqlalchemy import Column, Integer, String
from database import Base

# ---------------- Database Models ***Edit as needed*** ---------------- #
class Books(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    rating = Column(Integer)
    