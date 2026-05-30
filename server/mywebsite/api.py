from http import HTTPStatus

import structlog
from django.http import Http404, HttpRequest
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError

from account.routes import auth_router
from main.routes import (
    booking_router,
    legal_info_router,
    session_router,
    space_extra_stats_router,
    space_force_stop_router,
    space_info_router,
    space_router,
    space_stats_router,
    space_upload_camera_router,
)
from payments.routes import (
    convert_bonuses_router,
    payment_url_router,
    payment_webhook_router,
)

logger = structlog.get_logger(__name__)
api = NinjaAPI()


@api.exception_handler(ValidationError)
def api_validation_errors_handler(request: HttpRequest, exc: ValidationError):
    logger.error(
        'Validation error',
        errors=exc.errors,
        path=request.path,
        headers=request.headers,
    )
    return api.create_response(
        request,
        data={'detail': exc.errors},
        status=422,
    )


@api.exception_handler(HttpError)
def api_http_error_handler(request: HttpRequest, exc: HttpError):
    logger.error('API Error', exc=str(exc), code=int(exc.status_code))
    return api.create_response(
        request,
        {'detail': str(exc), 'success': False},
        status=exc.status_code,
    )


@api.exception_handler(Http404)
def api_404_error_handler(request: HttpRequest, exc: Http404):
    logger.error('API Error', exc=str(exc), code=404)
    return api.create_response(
        request,
        {'detail': 'Not Found', 'success': False},
        status=404,
    )


@api.exception_handler(Exception)
def api_exception_handler(request: HttpRequest, exc: Exception):
    code = getattr(exc, 'errno', HTTPStatus.INTERNAL_SERVER_ERROR)
    logger.exception('Unhandled error')
    return api.create_response(
        request,
        data={'detail': str(exc)},
        status=code,
    )


v1_path = '/v1/'
api.add_router(v1_path, space_router)
api.add_router(v1_path, space_stats_router)
api.add_router(v1_path, space_upload_camera_router)
api.add_router(v1_path, space_info_router)
api.add_router(v1_path, space_force_stop_router)
api.add_router(v1_path, auth_router)
api.add_router(v1_path, session_router)
api.add_router(v1_path, space_extra_stats_router)
api.add_router(v1_path, legal_info_router)
api.add_router(v1_path, convert_bonuses_router)
api.add_router(v1_path, payment_url_router)
api.add_router(v1_path, payment_webhook_router)
api.add_router(v1_path, booking_router)
