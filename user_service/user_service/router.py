# from fastapi import APIRouter,Depends
# from .schema import Creat_User
# from typing import Annotated
# from .db import get_session
# from aiokafka import AIOKafkaProducer # type: ignore
# from .crud import creat_user,produce_message
# from sqlmodel import Session



# user_router = APIRouter(
#                         prefix= "/user",
#             tags= ["User Router App"],
#                 responses= {404: {"description":"not found"}})



# @user_router.get("/router")
# async def router():
#     return {"message": "Hello from user router"}


# @user_router.post('/register/')
# async def register(user:Creat_User,
#                    producer:Annotated[AIOKafkaProducer,Depends(produce_message)],
#                    session:Annotated[Session,Depends(get_session)]):
#     signup_user= creat_user(user,session,producer)
#     try:
#         return signup_user
#     except Exception as e:
#         return {"message": f"An error occurred: {e}"}
    
