from .booking import router as booking_router
from .legal_info import router as legal_info_router
from .session import router as session_router
from .space import router as space_router
from .space_extra_stats import router as space_extra_stats_router
from .space_force_stop import router as space_force_stop_router
from .space_get_info import router as space_info_router
from .space_stats import router as space_stats_router
from .space_upload_camera import router as space_upload_camera_router

__all__ = [
    'booking_router',
    'legal_info_router',
    'space_router',
    'session_router',
    'space_extra_stats_router',
    'space_force_stop_router',
    'space_info_router',
    'space_stats_router',
    'space_upload_camera_router',
]
