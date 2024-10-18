from typing import Annotated
from fastapi import FastAPI, Depends,HTTPException
from sqlmodel import Session,select
from .db import get_session
from  .schema import User,update_user,RegisterUser
from passlib.context import CryptContext # type: ignore
from passlib.exc import UnknownHashError
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer # type: ignore
from .user_pb2 import Newuser # type: ignore

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

async def produce_message():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        # Produce message
        yield producer
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()


def verify_password(plain_password,password):
    try:
        
        return pwd_context.verify(plain_password,password)
    except UnknownHashError:
        print("Password hash could not be identified.")
def get_password_hash(password: str):
    return pwd_context.hash(password)

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-group",
        auto_offset_reset='earliest'
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Received message: {message.value.decode()} on topic {message.topic}")
            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()



async def db_user(session: Annotated[Session, Depends(get_session)],
                   username: str | None = None,
                   email: str | None = None):
    statement = select(User).where(User.userName == username)
    user = session.exec(statement).first()
    
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
    return user

async def auth_user(username:str| None ,password:str,
                     session: Annotated[Session, Depends(get_session)]
                                    ):
    data_user = await db_user(session=session,username=username)
    if not data_user:
        return False
    if not verify_password(password,data_user.password):
        return False
    return data_user
async def register_user(user:RegisterUser , session: Annotated[Session, Depends(get_session)],
                        producer:Annotated[AIOKafkaProducer,Depends(produce_message)]):
    existing_user = await db_user(username=user.user_name, email=user.email, session=session)  # Corrected call
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(userName=user.user_name, email=user.email, password=get_password_hash(user.password))
    user_data =Newuser(userName=new_user.userName, email=new_user.email)
    serialized_user = user_data.SerializeToString()
    await producer.send_and_wait('userService', serialized_user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


async def user_patch_update(statement,edit_user):
    if edit_user.user_name is not None and edit_user.user_name != "":
        statement.user_name = edit_user.user_name
    if edit_user.email is not None and edit_user.email != "":
        statement.email = edit_user.email
    if edit_user.password is not None and edit_user.password != "":
        statement.password = get_password_hash(edit_user.password)
    return statement
        
