from sqlmodel import SQLModel, Field


class User(SQLModel,table=True):
    id: int = Field(default=None,primary_key=True)
    userName: str = Field(index=True)
    email: str = Field(index=True)
    password: str
    
class Creat_User(SQLModel):
    userName: str 
    email: str 
    password: str
    