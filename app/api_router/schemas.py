from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Optional


class Response(BaseModel):
    status: str
    comment: Optional[str] = None


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_blacklist: bool = False


class UserResponse(UserBase):
    id: UUID
    status: int


class EventBase(BaseModel):
    title: str
    # Раздел мероприятия: business / family
    section: str = "business"
    description: str 
    participation_conditions: str
    location: str
    start_datetime: datetime
    timezone: str
    price: float
    max_participants: int
    status: str


class EventResponse(EventBase):
    id: int
    participants: int


class PermissionEnum(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    FORBIDDEN = "forbidden"


class AdminLogin(BaseModel):
    login: str
    password: str


class AdminCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    super_user: bool = False
    events: PermissionEnum = PermissionEnum.FORBIDDEN
    registers: PermissionEnum = PermissionEnum.FORBIDDEN
    partners_apply: PermissionEnum = PermissionEnum.FORBIDDEN
    exhibitions_apply: PermissionEnum = PermissionEnum.FORBIDDEN
    users: PermissionEnum = PermissionEnum.FORBIDDEN
    queue: PermissionEnum = PermissionEnum.FORBIDDEN
    payments: PermissionEnum = PermissionEnum.FORBIDDEN
    documents: PermissionEnum = PermissionEnum.FORBIDDEN
    reviews: PermissionEnum = PermissionEnum.FORBIDDEN
    notifications: PermissionEnum = PermissionEnum.FORBIDDEN
    support: PermissionEnum = PermissionEnum.FORBIDDEN
    qr_codes: PermissionEnum = PermissionEnum.FORBIDDEN


class AdminUpdate(BaseModel):
    login: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    super_user: Optional[bool] = None
    events: Optional[PermissionEnum] = None
    registers: Optional[PermissionEnum] = None
    partners_apply: Optional[PermissionEnum] = None
    exhibitions_apply: Optional[PermissionEnum] = None
    users: Optional[PermissionEnum] = None
    queue: Optional[PermissionEnum] = None
    payments: Optional[PermissionEnum] = None
    documents: Optional[PermissionEnum] = None
    reviews: Optional[PermissionEnum] = None
    notifications: Optional[PermissionEnum] = None
    support: Optional[PermissionEnum] = None
    qr_codes: Optional[PermissionEnum] = None


class AdminResponse(BaseModel):
    id: UUID
    login: str
    super_user: bool
    events: str
    registers: str
    partners_apply: str
    exhibitions_apply: str
    users: str
    queue: str
    payments: str
    documents: str
    reviews: str
    notifications: str
    support: str
    qr_codes: str
    

class AdminTokenData(BaseModel):
    """Данные в JWT токене"""
    login: str
    super_user: bool
    permissions: Dict[str, str]


