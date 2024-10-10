from typing import Annotated
from sqlmodel import Session,select
from fastapi import Depends,HTTPException
from .schema import Creat_User, User
from .db import get_session
from passlib.context import CryptContext # type: ignore
from aiokafka import AIOKafkaProducer # type: ignore
from starlette.config import Config
from . import user_pb2
pwd_context = CryptContext(schemes=["bcrypt"])
config = Config()

KAFKA_PRODUCER_TOPIC = "user service"
async def password_verfy(palin_password, hash_password):
    return pwd_context.verify(palin_password,hash_password)

async def hash_password(password):
    return pwd_context.hash(password)
async def produce_message():
    producer = AIOKafkaProducer(bootstrap_servers='localhost:19092')
    await producer.start()
    try:
        yield producer
        
    finally:
        await producer.stop()
    

async def current_user(user:Annotated[Creat_User,Depends()],
                       session:Annotated[Session,Depends(get_session)]):
    existing_user = session.exec(
        select(User).where(User.userName == user.userName)).first()
    if  existing_user:
        raise HTTPException(status_code=404, detail="User already exists")
    existing_email = session.exec(
        select(User).where(User.email == user.email)).first()
    if existing_email:
        raise HTTPException(status_code=404, detail="Email already exists")
    return user

async def creat_user(user:Annotated[Creat_User,Depends(current_user)],
                        session:Annotated[Session,Depends(get_session)],
                        producer:Annotated[AIOKafkaProducer,Depends(produce_message)]):
    hashed_password = await hash_password(user.password)
    new_user = User(userName=user.userName,email=user.email,password=hashed_password)
    userpb=user_pb2.User(userName=new_user.userName,email=new_user.email)
    serialized_data= userpb.SerializeToString()
    await producer.send_and_await(KAFKA_PRODUCER_TOPIC,serialized_data)
    print(userpb,serialized_data)
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
      