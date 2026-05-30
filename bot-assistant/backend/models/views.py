from typing import Optional, List

from pydantic import BaseModel


class ConnectorView(BaseModel):
    current_a: int
    phases_count: int
    power_kw: int
    type: str


class SpaceView(BaseModel):
    id: int
    lot: str
    name: str
    position: int
    price_kwh: int
    price_parking: int
    status: str  # see SPACE_STATUSES
    booked_until: Optional[int]
    connectors: List[ConnectorView]