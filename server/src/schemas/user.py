from pydantic import BaseModel


import uuid
from datetime import datetime


class usermodel(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    password: str

class UserCreate(BaseModel):
    username: str
    email : str
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime

class UserLogin(BaseModel):
    email : str
    password : str

class UserUpdate(BaseModel):
    username: str
    email: str

class ChangePass(BaseModel):
    old_password: str
    new_password: str
