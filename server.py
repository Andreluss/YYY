"""
Run with the following command:
uvicorn server:app --reload --port 8081
"""
# -------------------------------------------------------------------------------- #
# -------------------------------- Boilerplate ----------------------------------- #
# -------------------------------------------------------------------------------- #
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

# ^^^^^^^^^^^^^^^^^^^ standard CRUD operations ^^^^^^^^^^^^^^^^^^^ #
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


# ^^^^^^^^^^^^^^^^^^^^^^^^^^ websockets ^^^^^^^^^^^^^^^^^^^^^^^^^^ #

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