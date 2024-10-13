import datetime
from enum import Enum
import pydantic

from enum import Enum
from typing import Optional
import pydantic


DEFAULT_START_TIME = datetime.date.today()
DEFAULT_END_TIME = DEFAULT_START_TIME + datetime.timedelta(days=2)


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
    start_time: datetime.date = DEFAULT_START_TIME
    end_time: datetime.date = DEFAULT_END_TIME
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
    start_time: datetime.date = DEFAULT_START_TIME
    end_time: datetime.date = DEFAULT_END_TIME
    reward: str
    status: str
    contest_coins: str
    trading_balance: str

    class Config:
        from_attributes = True
