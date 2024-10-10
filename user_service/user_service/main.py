# import logging
from fastapi import FastAPI,Depends,HTTPException
# from .router import user_router
from typing import Annotated
from contextlib import asynccontextmanager
# from passlib.context import CryptContext # type: ignore
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer # type: ignore
from .schema import User,Creat_User
# from .db import get_session
from . import user_pb2
import asyncio
import json
# from sqlmodel import Session,select

# pwd_context = CryptContext(schemes=["bcrypt"])


async def consumer(topic,broker):
    consumer= AIOKafkaConsumer(
        topic , bootstrap_servers = broker,
        group_id = 'mygroup',
        auto_offset_reset='earliest',
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(f'{msg.topic},{msg.value}')
    finally:
        await consumer.stop()
    






# KAFKA_PRODUCER_TOPIC = "user service"
# async def password_verfy(palin_password, hash_password):
#     return pwd_context.verify(palin_password,hash_password)

# async def hash_password(password):
#     return pwd_context.hash(password)
# async def produce_message():
#     producer = AIOKafkaProducer(bootstrap_servers='localhost:9092')
#     await producer.start()
#     try:
#         yield producer
        
#     finally:
#         await producer.stop()
    

# async def current_user(user:Annotated[Creat_User,Depends()],
#                        session:Annotated[Session,Depends(get_session)]):
#     existing_user = session.exec(
#         select(User).where(User.userName == user.userName)).first()
#     if  existing_user:
#         raise HTTPException(status_code=404, detail="User already exists")
#     existing_email = session.exec(
#         select(User).where(User.email == user.email)).first()
#     if existing_email:
#         raise HTTPException(status_code=404, detail="Email already exists")
#     return user

# async def creat_user(user:Annotated[Creat_User,Depends(current_user)],
#                         session:Annotated[Session,Depends(get_session)],
#                         producer:Annotated[AIOKafkaProducer,Depends(produce_message)]):
#     hashed_password = await hash_password(user.password)
#     new_user = User(userName=user.userName,email=user.email,password=hashed_password)
#     userpb=user_pb2.Newuser(userName=new_user.userName,email=new_user.email)
#     serialized_data= userpb.SerializeToString()
    
#     print(userpb,serialized_data)
#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)
#     return new_user
@asynccontextmanager
async def lifespan(app:FastAPI):
    print("lifespan event")
    task = asyncio.create_task(consumer("service",'broker:19092'))
    yield  


app = FastAPI(lifespan=lifespan)
# app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "welcome to user service"}


@app.post('/register')
async def register(user:Creat_User):
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    user_json = json.dumps(user.__dict__).encode("utf_8")
    await producer.start()
    try:
        producer.send_and_wait("service",user_json)
    finally:
        await producer.stop()
    return {"message": "user registered successfully"}







# @app.post('/regiteruser/')
# async def register(user:Creat_User,
#                    producer:Annotated[AIOKafkaProducer,Depends(produce_message)],
#                    session:Annotated[Session,Depends(get_session)]):
#     signup_user= creat_user(user,session,producer)
#     try:
#         return signup_user
#     except Exception as e:
#         logging.error(f"Error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")