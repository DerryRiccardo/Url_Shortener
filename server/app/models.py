from datetime import datetime
from pydantic import EmailStr
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import Index
import uuid

class Role(Enum):
    admin = "admin"
    user = "user"

class Mode(Enum):
    random = "random"
    custom = "custom"

class UserBase(SQLModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(unique=True, index=True)

class User(UserBase, table = True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    role: Role = Field(default=Role.user)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UrlBase(SQLModel):
    long_url: str = Field(max_length=2048)
    title: str | None = Field(default=None, max_length=255)
    expires_at: datetime | None = Field(default=None)

class Url(UrlBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    alias: str = Field(max_length=50, index=True, unique=True)
    alias_mode: Mode = Field(default=Mode.random)
    is_active: bool = Field(default=True)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UrlCreate(UrlBase):
    alias_mode: Mode = Field(default=Mode.random)
    alias: str | None = Field(default=None, max_length=50)

class UrlUpdate(SQLModel):
    alias: str | None = Field(default=None, max_length=50)
    title: str | None = Field(default=None, max_length=255)
    expires_at: datetime | None = Field(default=None)

class UrlPublic(UrlBase):
    id: uuid.UUID
    alias: str
    short_url: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ClickEventBase(SQLModel):
    clicked_at: datetime = Field(default_factory=datetime.now)
    ip_hash: str | None = Field(default=None)
    user_agent: str | None = Field(default=None)
    referrer: str | None = Field(default=None)
    browser: str | None = Field(default=None)
    os: str | None = Field(default=None)
    device_type: str | None = Field(default=None)

class ClickEvent(ClickEventBase, table=True):
    __table_args__ = (Index("idx_url_id_clicked_at", "url_id", "clicked_at"),)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url_id: uuid.UUID = Field(foreign_key="url.id")

class QrCodeShared(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    qr_color: str = Field(default="#000000", max_length=7)

class QrCodeBase(QrCodeShared):
    target_url: str = Field(max_length=2048)
    qr_image: str = Field(max_length=255) 
    is_active: bool = Field(default=True)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class QrCode(QrCodeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    short_url_id: uuid.UUID | None = Field(default=None, foreign_key="url.id", index=True)

class QrCodeCreate(QrCodeShared):
    url_id: uuid.UUID | None = Field(default=None)
    long_url: str | None = Field(default=None, max_length=2048)

class QrCodePublic(QrCodeShared):
    id: uuid.UUID
    target_url: str
    short_url_id: uuid.UUID | None
    is_active: bool
    qr_image: str
    created_at: datetime
    updated_at: datetime

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

class ClickByDate(SQLModel):
    date: str
    clicks: int

class TopReferrer(SQLModel):
    referrer: str | None
    clicks: int

class DeviceStats(SQLModel):
    device_type: str | None
    clicks: int

class BrowserStats(SQLModel):
    browser: str | None
    clicks: int

class AnalyticsResponse(SQLModel):
    url_id: uuid.UUID
    alias: str
    total_clicks: int
    unique_visitors: int
    clicks_by_date: list[ClickByDate]
    top_referrers: list[TopReferrer]
    devices: list[DeviceStats]
    browsers: list[BrowserStats]

class AdminSummaryResponse(SQLModel):
    total_users: int
    total_urls: int
    active_urls: int
    inactive_urls: int
    total_qr_codes: int
    total_clicks: int
