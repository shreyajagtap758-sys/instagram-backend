from pydantic import BaseModel, EmailStr, field_validator, Field
import uuid
from datetime import datetime



class UserCreate(BaseModel):
    username: str
    email : EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime

class UserLogin(BaseModel):
    email : str = EmailStr
    password : str

class UserUpdate(BaseModel):
    username: str | None
    email: str = EmailStr | None

class get_refresh_token(BaseModel):
    refresh : str
