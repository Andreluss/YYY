"""
Run with the following command:
uvicorn server:app --reload --port 8081
"""
# -------------------------------------------------------------------------------- #
# -------------------------------- Boilerplate ----------------------------------- #
# -------------------------------------------------------------------------------- #
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

# --------------- fast api config [DON'T TOUCH] --------------- #
app = FastAPI()

# ------ Enable CORS ------ #
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ database config [DON'T TOUCH] ------------------ #
# this will create the db and tables if they don't exist
models.Base.metadata.create_all(bind=engine) 

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------- #
# -------------------------------------------------------------------------------- #




# ------------------ API Models ***Edit as needed*** ------------------ #
# -------------------------------------------------------------------------------- #
class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)
    

# ------------------ API Endpoints ***Edit as needed*** ------------------ #
# -------------------------------------------------------------------------------- #

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return db.query(models.Books).all()

@app.post("/")
def create_book(book: Book, db: Session = Depends(get_db)):
    # tworzymy obiekt modelu z bazy danych
    book_model = models.Books(title=book.title, author=book.author, description=book.description, rating=book.rating)
    # teraz trzeba go spushować do bazy danych
    db.add(book_model)
    # i zapisać zmiany(!)
    db.commit()
    
    return book

@app.put("/{book_id}")
def update_book(book_id: int, book: Book, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating
    db.commit()
    return book

    
@app.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    
    db.delete(book_model)
    db.commit()
    return f"Book with id {book_id} deleted"

