from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Annotated,Optional
from fastapi import Form

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userName: str
    email:str
    password: str
class update_user(BaseModel):
    user_name: str|None = None
    email:str|None = None
    password: str|None = None 
    
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
    
class RegisterUser(BaseModel):
    
        user_name : Annotated[
            str,
            Form()
        ]
        email : Annotated[
            str,
            Form()
        ]
        password : Annotated[
            str,
            Form()
        ]
        
class token(BaseModel):
    access_token: str
    token_type: str