from http import HTTPStatus
from typing import List

from ninja import Router
from ninja.errors import HttpError

from account.auth.bearer_token import AuthBearerUser
from chat.presenters.refill import SpaceView, present_space
from main.models.parking_space import ParkingSpace

router = Router()


@router.get(
    path='/space/{space_id}/',
    response=SpaceView,
    auth=AuthBearerUser(),
)
def get_space(request, space_id: int):
    try:
        space: ParkingSpace = ParkingSpace.objects.get(id=space_id)
    except ParkingSpace.DoesNotExist as not_found_err:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            'Парковочное место не найдено',
        ) from not_found_err

    return present_space(space)


@router.get(
    path='/space/all',
    response=List[SpaceView],
    auth=AuthBearerUser(),
)
def all_spaces(request):
    try:
        spaces = ParkingSpace.objects.all()
        present_spaces: List[SpaceView] = list(map(lambda space: present_space(space) ,[space for space in spaces]))
    except ParkingSpace.DoesNotExist as not_found_err:
        raise HttpError(
            HTTPStatus.NOT_FOUND,
            'Парковочных мест нет'
        ) from not_found_err

    return present_spaces
