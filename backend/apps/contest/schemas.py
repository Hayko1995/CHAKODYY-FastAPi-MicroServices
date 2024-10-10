import datetime
from enum import Enum
import pydantic

from enum import Enum
from typing import Optional
import pydantic


class CategoryEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class StatusEnum(str, Enum):
    upcoming = "upcoming"
    active = "active"
    closed = "closed"


class CreateContest(pydantic.BaseModel):
    title: str
    category: CategoryEnum = CategoryEnum.weekly
    start_time: datetime.date
    end_time: datetime.date
    reward: str
    contest_coins: str
    trading_balance: str
    status: StatusEnum = StatusEnum.upcoming

    class Config:
        from_attributes = True


class UpdateContest(pydantic.BaseModel):
    id: Optional[int] = -1
    title: str
    category: CategoryEnum = CategoryEnum.weekly
    start_time: datetime.date
    end_time: datetime.date
    reward: str
    status: str
    contest_coins: str
    trading_balance: str

    class Config:
        from_attributes = True
