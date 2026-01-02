from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Meeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    participants: Optional[str] = None # Comma separated list of names
