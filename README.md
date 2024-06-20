# Template for FastAPI applications 

Contains examples for 
- Create/Read/Update/Delete Endpoints
- Websockets
- Database boilerplate: [models.py](https://github.com/Andreluss/YYY/blob/main/models.py), [database.py](https://github.com/Andreluss/YYY/blob/main/database.py) (generates the `database.db` file)

Run the server with:
``` 
uvicorn server:app --reload --port 8081
```

Seed the database with some initial data by visiting http://localhost:8081/seed-database

