from typing import TypedDict, Optional, List
from datetime import datetime
from enum import Enum


class RentalStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class RentalType(TypedDict):
    id: Optional[int]
    customer_id: int
    car_id: int
    start_date: datetime
    end_date: datetime
    actual_return_date: Optional[datetime]
    daily_rate: float
    total_price: float
    status: RentalStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class RentalCreateType(TypedDict):
    customer_id: int
    car_id: int
    start_date: str  
    end_date: str  
    extras: Optional[List[str]]  


class RentalUpdateType(TypedDict, total=False):
    start_date: Optional[str]
    end_date: Optional[str]
    status: Optional[RentalStatus]
    actual_return_date: Optional[str]


class RentalStatusUpdateType(TypedDict):
    status: RentalStatus


class PriceCalculationType(TypedDict):
    daily_rate: float
    num_days: int
    base_price: float
    extras_cost: float
    total_price: float
