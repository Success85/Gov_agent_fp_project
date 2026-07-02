from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str = "ok"


class UserCreate(BaseModel):
    phone_number: str | None = None
    preferred_language: str = "en"


class UserRead(ORMModel):
    id: int
    phone_number: str | None
    preferred_language: str
    created_at: datetime


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    fee: float = 0


class ServiceRead(ORMModel):
    id: int
    name: str
    description: str | None
    fee: float
    is_active: bool


class ConversationCreate(BaseModel):
    user_id: int


class ConversationRead(ORMModel):
    id: int
    user_id: int
    status: str
    started_at: datetime


class MessageCreate(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class MessageRead(ORMModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime


class ApplicationCreate(BaseModel):
    user_id: int
    service_id: int
    conversation_id: int | None = None


class ApplicationRead(ORMModel):
    id: int
    user_id: int
    service_id: int
    conversation_id: int | None
    status: str
    reference_number: str
    created_at: datetime
    updated_at: datetime


class ApplicationDataUpsert(BaseModel):
    requirement_id: int
    value: str | None = None


class UploadRead(ORMModel):
    id: int
    application_id: int
    requirement_id: int | None
    file_path: str
    file_name: str | None
    uploaded_at: datetime


class PaymentCreate(BaseModel):
    payment_method: str
    amount: float
    gateway_reference: str | None = None


class PaymentRead(ORMModel):
    id: int
    application_id: int
    payment_method: str
    gateway_reference: str | None
    amount: float
    status: str
    created_at: datetime


class GeneratedDocumentRead(ORMModel):
    id: int
    application_id: int
    file_path: str
    generated_at: datetime
