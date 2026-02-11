from db.session import engine, Base
from db import models

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database Initialised")
