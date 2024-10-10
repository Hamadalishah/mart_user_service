from typing import Optional
from sqlmodel import SQLModel,create_engine, Session
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

connection_string:Optional[str] = os.getenv("DATABASEURL".replace(
    "postgresql", "postgresql+psycopg"))
if connection_string is None:
    raise ValueError("DATABASEURL is not set")


engine = create_engine(connection_string)


    
  
def create_table():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session