"""
Run with the following command:
uvicorn server:app --reload --port 8081
seed the database with some initial data by visiting http://localhost:8081/seed-database
"""
# -------------------------------------------------------------------------------- #
# -------------------------------- Boilerplate ----------------------------------- #
# -------------------------------------------------------------------------------- #
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
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
# this will create the db and tables if they don't exist (all table models from models.py)
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




# -------------------------------------------------------------------------------- #
# ------------------ API Models ***Edit as needed*** ------------------ #
# -------------------------------------------------------------------------------- #
class Book(BaseModel): # to jest api model, nie model z bazy danych (patrz models.py) 
    title: str = Field(min_length=1) # ten przydaje sie do walidacji api requestów
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)
    
# kolejny api model - do walidacji requestów, nie musi być coupled z modelem z bazy danych
class Review(BaseModel):
    review: str = Field(min_length=1, max_length=1000)
    rating: int = Field(gt=-1, lt=101)


# -------------------------------------------------------------------------------- #
# ------------------ API Endpoints ***Edit as needed*** -------------------------- #
# -------------------------------------------------------------------------------- #

# _________ _________ _________ _________ _________ _________ _________ _________ #
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ standard CRUD operations ^^^^^^^^^^^^^^^^^^^^^^^^^^ #
@app.get("/")
def get_all_books(db: Session = Depends(get_db)):
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
# _________ _________ _________ _________ _________ _________ _________ _________ #


# _________ _________ _________ _________ _________ _________ _________ _________ #
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ more CRUD operations ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ #
@app.get("/book_reviews/{book_id}")
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reviews).filter(models.Reviews.book_id == book_id).all()

@app.post("/book_reviews/{book_id}/{user_id}") # common practice is to use path params for (resource) ids 
def create_book_review(book_id: int, user_id: int, review: Review, db: Session = Depends(get_db)): 
    # ensure the user and book exist
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    
    review_model = models.Reviews(book_id=book_id, user_id=user_id, review=review.review, rating=review.rating)
    db.add(review_model)
    db.commit()
    return review

@app.get("/book_reviews/{book_id}/average_rating")
def get_book_average_rating(book_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Reviews).filter(models.Reviews.book_id == book_id).all()
    if len(reviews) == 0:
        return {"average_rating": 0}
    
    total_rating = sum([review.rating for review in reviews])
    return {"average_rating": total_rating / len(reviews)}

@app.get("/user_reviews/{user_id}")
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reviews).filter(models.Reviews.user_id == user_id).all()

class User(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    # email with regex validation
    email: str = Field(min_length=1, max_length=100, pattern="[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")
    password: str = Field(min_length=1, max_length=100)

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()

# endpoint for creating new user
@app.post("/users")
def create_user(user: User, db: Session = Depends(get_db)):
    user_model = models.Users(username=user.username, email=user.email, password=user.password)
    db.add(user_model)
    db.commit()
    return user

# seed the database with some initial data
@app.get("/seed-database")
def seed_database(db: Session = Depends(get_db)):
    # seed the database with some initial
    user1 = models.Users(username="user1", email="apud123@gmail.com", password="password123")
    user2 = models.Users(username="Zdzichu", email="zzz@gmail.com", password="hahahaha")
    db.add(user1)
    db.add(user2)

    book1 = models.Books(title="Harry Potter", author="J.K. Rowling", description="A book about a wizard", rating=90)
    book2 = models.Books(title="The Hobbit", author="J.R.R. Tolkien", description="A book about a hobbit", rating=95)
    db.add(book1)
    db.add(book2)

    # make sure the book.id and user.id are correct
    db.commit()
    print('New user id:', user1.id)
    print('New user id:', user2.id)
    print('New book id:', book1.id)
    print('New book id:', book2.id)

    review1 = models.Reviews(book_id=book1.id, user_id=user1.id, review="Great book", rating=90)
    review2 = models.Reviews(book_id=book1.id, user_id=user2.id, review="Good book", rating=80)
    review3 = models.Reviews(book_id=book2.id, user_id=user1.id, review="Great book", rating=90)
    review4 = models.Reviews(book_id=book2.id, user_id=user2.id, review="Good book", rating=80)

    db.add(review1)
    db.add(review2)
    db.add(review3)
    db.add(review4)

    db.commit()
    return "Database seeded"
# _________ _________ _________ _________ _________ _________ _________ _________ #




# _________ _________ _________ _________ _________ _________ _________ _________ #
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ websockets! ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ #

# ----------- typical manager for websockets [DON'T TOUCH] ---------- #
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        
    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket):
        self.active_connections.remove(websocket)
        
    async def send_personal_message(self, message, websocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


# ----------------- API Websocket Endpoints ***Edit as needed*** ----------------- #
# -------------------------------------------------------------------------------- #
html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>Websocket Demo</title>
           <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

    </head>
    <body>
    <div class="container mt-3">
        <h1>FastAPI WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" class="form-control" id="messageText" autocomplete="off"/>
            <button class="btn btn-outline-primary mt-2">Send</button>
        </form>
        <ul id='messages' class="mt-5">
        </ul>
        
    </div>
    
        <script>
            var client_id = Date.now() // LLLLLLLMMMMMMAAAAAAAAAAOOOOOOOOOO
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8081/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
@app.get("/ws-chat-demo")
async def get():
    return HTMLResponse(html2)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client {client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left the chat")