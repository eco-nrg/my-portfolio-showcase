from http import HTTPStatus
from logging import DEBUG, INFO
from typing import Any, Dict, Optional

import simplejson
import structlog
from asgiref.sync import async_to_sync
from channels.auth import login, logout
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from pydantic import ValidationError
from typing_extensions import TypedDict

from account.edit_profile import EditProfileForm, edit_profile
from account.models import Connection, Token
from account.reset_code import ResetCodeError, reset_code
from account.signup import signup
from chat.auth_helpers import authorized
from chat.authorisation import AuthError, auth_user_by_code
from chat.booking import (
    BookingError,
    BookSpaceParams,
    book_space,
    cancel_bookings,
)
from chat.charge_session import (
    StartSessionError,
    StartSessionParams,
    start_session,
)
from chat.event.booking import send_bookings, send_cancel_bookings
from chat.event.payment import (
    send_convert_bonuses_response,
    send_payment_url,
    send_payments,
)
from chat.event.phone_auth import send_phone_auth_response
from chat.event.profile import send_edit_profile_response, send_profile
from chat.event.refill import send_map, send_refills
from chat.event.session import (
    send_session_charging,
    send_session_stop,
    send_sessions_history,
    send_start_session_success,
)
from chat.orders_history import present_chart_influx
from chat.payment import GetPaymentsParams
from chat.stop_session import StopSessionError, stop_session
from payments.bonus import BonusError, ConvertBonusesRequest, convert_bonuses
from payments.services.models.exceptions import PaymentError
from payments.schemas import PaymentLinkRequest
from payments.services.payments_service import create_payment_link

logger = structlog.stdlib.get_logger(__name__)


class Event(TypedDict):
    type: str
    data: Any


def present_user(user: Optional[User]):
    if user is None:
        return None
    if user.is_anonymous:
        return None
    return str(user.username)


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'all'  # группа с авторизованными пользователями
        self.handlers = {
            'token_auth': self.token_auth_handler,
            'phone_auth': self.phone_auth_handler,
            'send_code': self.send_code_handler,
            'init': self.init_handler,
            'phone_check': self.phone_check_handler,
            'refill': self.refill_handler,
            'start_session': self.start_session_handler,
            'stop_session': self.stop_session_handler,
            'edit_profile': self.edit_profile_handler,
            'logout': self.logout_handler,
            'sessions_history': self.sessions_history_handler,
            'session_chart': self.session_chart_handler,
            'get_booking': self.get_booking_handler,
            'book_space': self.book_space_handler,
            'cancel_bookings': self.cancel_bookings_handler,
            'create_payment_url': self.create_payment_url_handler,
            'convert_bonuses': self.convert_bonuses_handler,
            'get_payments': self.get_payments_handler,
        }

    @property
    def user(self) -> Optional[User]:
        return self.scope.get('user')

    def connect(self):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            channel_name=self.channel_name,
            user=None,
        )
        Connection.objects.create(channel_name=self.channel_name)
        self.accept()
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        logger.info('connect')

    def disconnect(self, code):
        Connection.objects.filter(channel_name=self.channel_name).delete()
        logger.info('disconnect')

    def receive(self, text_data: str):
        if text_data == 'ping':
            # required by https://pub.dev/packages/websocket_universal
            return self.send('pong')

        try:
            message_json = simplejson.loads(text_data)
        except simplejson.JSONDecodeError:
            logger.exception('Malformed json message')
            return None
        msg_type = message_json.get('type', None)
        data = message_json.get('data', {})

        with structlog.contextvars.bound_contextvars(
            data=simplejson.dumps(data),
            type=msg_type,
        ):
            logger.info('receive')
            handler = self.handlers.get(msg_type)
            if handler is None:
                logger.warn('Unknown message type')
                # TODO: отправить пользователю сообщение об ошибке?
                return None

            try:
                handler(data=data)
            except Exception:
                # не отправляем пользователям ничего
                logger.exception('Unhandled error')

    def authenticate(self, user: User, token_value: str):
        structlog.contextvars.bind_contextvars(user=present_user(user))
        Connection.objects.filter(
            channel_name=self.channel_name,
        ).update(user=user)

        async_to_sync(login)(
            self.scope,
            user,
            backend='django.contrib.auth.backends.ModelBackend',
        )
        self.scope['token'] = token_value
        self.scope['session'].save()

    def authenticate_token(self, data) -> Optional[User]:
        token_value = data.get('token')
        if token_value is None:
            logger.warning('Empty token')
            self.send_error(
                message='Невозможно войти с предоставленным токеном',
                code=HTTPStatus.UNAUTHORIZED,
                request='init',
            )
            return None
        token = Token.objects.filter(key=token_value, is_active=True).first()
        if token is not None:
            user = token.user
            self.authenticate(user, token.key)
            return user

        self.send_error(
            message='Невозможно войти с предоставленным токеном',
            code=HTTPStatus.UNAUTHORIZED,
            request='init',
        )
        return None

    # --- handlers ---

    def init_handler(self, data):
        user = self.authenticate_token(data)
        if user is None:
            return

        send_profile(self.channel_name, user)
        send_session_charging(self.channel_name, user)
        send_phone_auth_response(self.channel_name, user, self.scope['token'])
        send_refills(self.channel_name)
        send_map(self.channel_name)
        send_sessions_history(self.channel_name, user)
        send_bookings(self.channel_name, user)
        send_payments(self.channel_name, user)

    def logout_handler(self, data=None):
        # TODO: deactivate token
        Connection.objects.filter(
            channel_name=self.channel_name,
        ).update(user=None)
        token = self.scope.get('token')
        if token is not None:
            self.scope['token'] = None
            Token.objects.filter(key=token).update(is_active=False)

        if self.user is not None:
            async_to_sync(logout)(self.scope)

        self.scope['session'].save()

    def send_code_handler(self, data):
        try:
            resp = reset_code(data)
        except ResetCodeError as err:
            return self.send_error(
                request='send_code',
                message=err.msg,
            )
        else:
            async_to_sync(self.channel_layer.send)(
                self.channel_name,
                {
                    'type': 'send_code_response',
                    'data': resp.dict(),
                },
            )

    def token_auth_handler(self, data):
        token_value = data.get('token')
        if token_value is None:
            logger.warning('Empty token')
            return self.send_error(
                message='Невозможно войти с предоставленным токеном',
                code=HTTPStatus.UNAUTHORIZED,
                request='token_auth',
            )

        token = Token.objects.filter(key=token_value).first()
        if token is not None:
            user = token.user
            return self.authenticate(user, token.key)

        return self.send_error(
            message='Невозможно войти с предоставленным токеном',
            code=HTTPStatus.UNAUTHORIZED,
            request='init',
        )

    def phone_auth_handler(self, data):
        try:
            user = auth_user_by_code(data.get('phone'), data.get('code'))
        except AuthError as err:
            return self.send_error(
                request='phone_auth',
                message=err.msg,
            )
        except Exception:
            return self.send_error(
                request='phone_auth',
                message='Невозможно войти с продоставленными данными',
            )

        token = Token.objects.create(user=user)
        self.authenticate(user, token.key)
        send_profile(self.channel_name, user)
        send_session_charging(self.channel_name, user)
        send_phone_auth_response(self.channel_name, user, token.key)
        send_refills(self.channel_name)
        send_map(self.channel_name)
        send_sessions_history(self.channel_name, user)
        send_bookings(self.channel_name, user)
        send_payments(self.channel_name, user)
        return None

    def phone_check_handler(self, data: Dict):
        resp = signup(data)
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'phone_check_response',
                'data': resp.dict(),
            },
        )

    def send_error(
        self,
        message: str,
        request: Optional[str] = None,
        errors: Optional[Any] = None,
        code: int = HTTPStatus.BAD_REQUEST,
    ):
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'error_response',
                'success': False,
                'code': code,
                'data': {
                    'message': message,
                    'errors': errors,
                    'request': request,
                },
            },
        )

    @authorized
    def get_booking_handler(self, data):
        try:
            send_bookings(self.channel_name, self.user, send_none=True)
        except BookingError as err:
            return self.send_error(
                message=err.msg,
                request='get_booking',
            )

    @authorized
    def book_space_handler(self, data):
        token_value = self.scope.get('token')

        try:
            book_params = BookSpaceParams.parse_obj(data)
        except ValidationError as val_err:
            return self.send_error(
                message='Неверный формат запроса',
                errors=val_err.errors(),
                request='book_space',
            )
        try:
            book_space(self.user, book_params)
        except BookingError as book_err:
            return self.send_error(
                message=book_err.msg,
                request='book_space',
            )
        else:
            send_bookings(self.user, self.user)
            send_refills(self.room_group_name)
            send_phone_auth_response(self.user, self.user, token_value)

    @authorized
    def cancel_bookings_handler(self, data):
        token_value = self.scope.get('token')

        try:
            cancel_bookings(self.user)
            send_cancel_bookings(self.user)
            send_refills(self.room_group_name)
            send_phone_auth_response(self.user, self.user, token_value)
        except BookingError as err:
            self.send_error(
                message=err.msg,
                request='cancel_bookings',
            )

    @authorized
    def start_session_handler(self, data):
        try:
            session_params = StartSessionParams.parse_obj(data)
        except ValidationError as val_err:
            return self.send_error(
                message='Неверный формат запроса',
                errors=val_err.errors(),
                request='start_session',
            )
        try:
            start_session(
                params=session_params,
                user=self.user,
            )
        except StartSessionError as sess_err:
            return self.send_error(
                message=sess_err.msg,
                request='start_session',
            )

        send_start_session_success(self.user, self.user)
        send_session_charging(self.user, self.user)
        send_refills(self.room_group_name)
        send_sessions_history(self.user, self.user)
        send_phone_auth_response(self.user, self.user)
        # так как активация бронирования подразумевает, что бронирования сняты
        send_cancel_bookings(self.user)
        return None

    @authorized
    def stop_session_handler(self, data=None):
        token_value = self.scope.get('token')

        try:
            res = stop_session(self.user)
        except StopSessionError as err:
            return self.send_error(
                message=err.msg,
                request='stop_session',
            )

        send_session_stop(self.user, space_id=res['id'])
        send_refills(self.room_group_name)
        send_phone_auth_response(self.user, self.user, token_value)
        send_sessions_history(self.user, self.user)
        return None

    @authorized
    def refill_handler(self, data=None):
        send_refills(self.channel_name)

    @authorized
    def session_chart_handler(self, data):
        try:
            chart = present_chart_influx(self.user, data.get('order_uuid'))
        except Exception:
            logger.error('Failed to get chart')
            chart = None

        if chart is None:
            return self.send_error(
                message='Заказ не найден',
                request='session_chart',
            )

        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'session_chart_response',
                'data': chart,
            },
        )
        return None

    @authorized
    def sessions_history_handler(self, data=None):
        send_sessions_history(self.channel_name, self.user)

    @authorized
    def edit_profile_handler(self, data):
        try:
            edit_form = EditProfileForm.parse_obj(data)
        except ValidationError as err:
            return self.send_error(
                message='Неверный формат запроса',
                errors=err.errors(),
                request='start_session',
            )
        edit_profile(edit_form, self.user)
        send_profile(self.user, self.user)
        send_edit_profile_response(self.user)
        return None

    @authorized
    def create_payment_url_handler(self, data):
        try:
            request = PaymentLinkRequest.parse_obj(data)
        except ValidationError as validation_err:
            return self.send_error(
                message='Неверный формат запроса',
                errors=validation_err.errors(),
                request='create_payment_url',
            )
        try:
            payment_url = create_payment_link(self.user, request.amount)
        except PaymentError as err:
            return self.send_error(
                message=err.msg,
                request='create_payment_url',
            )
        except Exception:
            return self.send_error(
                message='Попробуйте повторить операцию позже',
                request='create_payment_url',
            )

        send_payment_url(self.user, payment_url)
        return None

    @authorized
    def convert_bonuses_handler(self, data):
        token_value = self.scope.get('token')

        try:
            request = ConvertBonusesRequest.parse_obj(data)
        except ValidationError as validation_err:
            return self.send_error(
                message='Неверный формат запроса',
                errors=validation_err.errors(),
                request='convert_bonuses',
            )
        try:
            res = convert_bonuses(self.user, request)
        except BonusError as bonus_err:
            return self.send_error(
                message=bonus_err.msg,
                request='convert_bonuses',
            )

        send_convert_bonuses_response(self.user, res)
        send_phone_auth_response(self.user, self.user, token_value)
        return None

    @authorized
    def get_payments_handler(self, data):
        try:
            get_payments_param = GetPaymentsParams.parse_obj(data)
        except ValidationError as err:
            return self.send_error(
                message='Неверный формат запроса',
                errors=err.errors(),
                request='get_payments',
            )
        send_payments(self.user, self.user, get_payments_param)
        return None

    # --- responses ---

    def _just_send(self, event: Event, level: int = INFO):
        if event['type'] == 'error_response':
            logger.log(level, 'send', type=event['type'], data=event.get('data'))
        else:
            logger.log(level, 'send', type=event['type'])
        self.send(
            text_data=simplejson.dumps(
                {
                    'type': event['type'],
                    'data': event.get('data'),
                    'code': event.get('code', 200),
                },
            ),
        )

    def init_response(self, event: Event):
        self._just_send(event)

    def auth_response(self, event: Event):
        self._just_send(event)

    def phone_check_response(self, event: Event):
        self._just_send(event)

    def phone_auth_response(self, event: Event):
        self._just_send(event)

    def send_code_response(self, event: Event):
        self._just_send(event)

    def profile_response(self, event: Event):
        self._just_send(event)

    def edit_profile_response(self, event: Event):
        self._just_send(event)

    def refill_response(self, event: Event):
        self._just_send(event)

    def error_response(self, event: Event):
        self._just_send(event)

    def start_session_success(self, event: Event):
        self._just_send(event)

    def session_charging(self, event: Event):
        self._just_send(event)

    def session_stop(self, event: Event):
        self._just_send(event)

    def map_response(self, event: Event):
        self._just_send(event)

    def sessions_history_response(self, event: Event):
        self._just_send(event)

    def session_chart_response(self, event: Event):
        self._just_send(event)

    def book_space_response(self, event: Event):
        self._just_send(event)

    def cancel_booking_response(self, event: Event):
        self._just_send(event)

    def cancel_bookings_response(self, event: Event):
        self._just_send(event)

    def payment_url_response(self, event: Event):
        self._just_send(event)

    def convert_bonuses_response(self, event: Event):
        self._just_send(event)

    def get_payments_response(self, event: Event):
        self._just_send(event)

    def payment_response(self, event: Event):
        self._just_send(event)

    def ping_response(self, event: Event):
        self._just_send(event, level=DEBUG)
