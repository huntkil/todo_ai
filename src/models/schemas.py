from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CalendarEventCreate(BaseModel):
    summary: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    user_id: str


class CalendarEventOut(BaseModel):
    id: int
    summary: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True


class ObsidianNoteCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    user_id: str


class ObsidianNoteOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True


class GanttTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str = "pending"
    priority: str = "medium"
    user_id: str


class GanttTaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str
    priority: str
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    name: str
    # email: Optional[str] = None  # deprecated
    # phone: Optional[str] = None  # deprecated
    emails: Optional[list[str]] = None
    phones: Optional[list[str]] = None
    company: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None
    user_id: str


class ContactOut(BaseModel):
    id: int
    name: str
    # email: Optional[str] = None  # deprecated
    # phone: Optional[str] = None  # deprecated
    emails: Optional[list[str]] = None
    phones: Optional[list[str]] = None
    company: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_id: str

    class Config:
        from_attributes = True
