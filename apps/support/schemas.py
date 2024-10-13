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


class CreateTicketRequest(pydantic.BaseModel):
    status: TicketEnum
    text: str
    request_type: RequestEnum

    class Config:
        from_attributes = True


class UpdateTicketRequest(pydantic.BaseModel):
    id: int
    text: str
    action_owner: int
    status: TicketEnum
    request_type: RequestEnum
    subject: str

    class Config:
        from_attributes = True

class GetTickets(pydantic.BaseModel):
    id:  Optional[int] 
    status: Optional[str] 
    
class GetTicketHistory(pydantic.BaseModel):
    ticket_number:  Optional[int] 