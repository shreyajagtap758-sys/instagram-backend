from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
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
    username: str | None = None
    is_private: bool | None = None

class UpdateAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    is_private: bool

class get_refresh_token(BaseModel):
    refresh : str

class delete_account(BaseModel):
    status: str
    deleted_at: datetime
    deletion_scheduled_for: datetime
    restore_window_days: int
    already_pending_deletion: bool

class restore_account(BaseModel):
    status: str
    restored: bool
    already_restored: bool
