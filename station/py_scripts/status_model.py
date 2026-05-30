from pydantic import BaseModel
from typing import Optional, Union


class Status(BaseModel):
    state: Optional[str]
    response: str
    am: Optional[float]
    current_kwh: Optional[float]
    chargingStation: Optional[str]
    url: Optional[str]
    sliderCounts: Optional[int]
    timerSlideChange: Optional[int]
    total_kwh: Optional[float]
    created_at: Optional[int]
    start_payed: Union[int, None]
    freeTime: Optional[int]
    booked_until: Optional[int]
