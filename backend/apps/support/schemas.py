import pydantic

from enum import Enum
from typing import Optional


class UserBase(pydantic.BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True


class TicketEnum(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    WARNING = "warning"
    ISSUE = "issue"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    

class RequestEnum(str, Enum):
    issue = "Technical Issue"
    frequest = "Feature Request"
    generel_equiry = "General Enquiry"
    feedback = "Feedback"


class Ticket(pydantic.BaseModel):
    id: Optional[int] = -1
    status: TicketEnum = TicketEnum.ACTIVE
    text: str
    request_type: RequestEnum = RequestEnum.generel_equiry

    class Config:
        from_attributes = True
