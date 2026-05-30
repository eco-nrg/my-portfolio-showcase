from http import HTTPStatus

from ninja import Router, Schema
from ninja.errors import HttpError

from account.models import Token
from account.reset_code import ResetCodeError, ResetCodeResponse, reset_code
from account.signup import SignupResponse, signup
from chat.authorisation import AuthError, auth_user_by_code

router = Router(tags=['users'])


class AuthWithPhoneRequest(Schema):
    phone: str
    code: str


class LoginResponse(Schema):
    # auth for back compatibility with phone_auth in ws
    # actually it's token
    auth: str


class SignupRequest(Schema):
    phone: str


class ResendCodeRequest(Schema):
    phone: str


@router.post(
    path='/auth/login',
    response=LoginResponse,
)
def login_with_phone_endpoint(
    request,
    data: AuthWithPhoneRequest,
):
    try:
        user = auth_user_by_code(data.phone, data.code)
    except AuthError as auth_err:
        raise HttpError(HTTPStatus.UNAUTHORIZED, auth_err.msg) from auth_err
    except Exception as err:
        raise HttpError(
            HTTPStatus.UNAUTHORIZED,
            'Невозможно войти с предоставленными данными',
        ) from err

    token = Token.objects.create(user=user)
    return LoginResponse(auth=token.key)


@router.post(
    path='/auth/signup',
    response=SignupResponse,
)
def signup_endpoint(request, data: SignupRequest):
    res = signup({'phone': data.phone})
    if res.code != HTTPStatus.OK:
        raise HttpError(
            res.code,
            res.detail,
        )
    return res


@router.post(
    path='/auth/resend_code',
    response=ResetCodeResponse,
)
def resend_code_endpoint(request, data: ResendCodeRequest):
    try:
        return reset_code({'phone': data.phone})
    except ResetCodeError as err:
        raise HttpError(
            HTTPStatus.BAD_REQUEST,
            err.msg,
        ) from err
