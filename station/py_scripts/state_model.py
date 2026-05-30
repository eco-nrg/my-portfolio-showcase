from pydantic import BaseModel
from typing import Optional

# State
# The State class represents a model for storing and manipulating various
# attributes related to state station.
# Model is used for:
# - send data to grafana


class State(BaseModel):
    state: Optional[str]
    state_val: Optional[int]
    no_internet: Optional[int]
    no_internet_iter: Optional[int]
    no_internet_time: Optional[str]
    has_power: Optional[int]
    real_has_power: Optional[int]
    parklock_last_status: Optional[str]
    parklock_need_status: Optional[str]
    parklock_manual_mode: Optional[int]
    wait_time: Optional[str]
    current_a: Optional[float]
    current_a_phase_1: Optional[float]
    current_a_phase_2: Optional[float]
    current_a_phase_3: Optional[float]
    current_w: Optional[float]
    sonic_range: Optional[float]
    sonic_range_avg: Optional[float]
    sonic_last_time: Optional[int]
    lidar_distance: Optional[float]
    lidar_last_time: Optional[int]
    reed_value: Optional[int]
    total_kw: Optional[float]
    order_id: Optional[str]
    user: Optional[str]
    space_status: Optional[str]
