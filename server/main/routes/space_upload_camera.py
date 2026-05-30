import os
import shutil
from http import HTTPStatus

from django.conf import settings
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from account.auth.bearer_token import AuthBearerDevice, AuthBearerUser
from main.models import Camera, get_image_path

router = Router(tags=['devices'])

CAMERA_ITER_CIRCLE_SIZE = 360


def get_static_pathes(camera: Camera, ext='jpg'):
    pathes = []
    if camera.space:
        space_id = camera.space.id
        pathes.append(f'camera/space/{space_id}.{ext}')
    if camera.send_by_space:
        lot_id = camera.lot.id
        pathes.append(f'camera/refill/{lot_id}.{ext}')

    return [os.path.join(settings.MEDIA_ROOT, p) for p in pathes]


def copy_to_static_place(abs_path: str, camera: Camera):
    """
    Copy media file.

    /media/camera/refill/:refill_id:
    /media/camera/space/:space_id:
    """
    pathes = get_static_pathes(camera, ext='jpg')
    for p in pathes:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy(abs_path, p)


@router.post(
    path='/upload_camera_image/{camera_id}/',
    # TODO: убрать AuthBearerUser когда станции переведем на AuthBearerDevice
    auth=[AuthBearerDevice(), AuthBearerUser()],
)
def upload_camera_image(request, camera_id: int):
    # TODO: should we check this device is able to upload this camera's image?
    camera = Camera.objects.get(id=camera_id)

    file = request.FILES.get('image')
    if file is None:
        raise HttpError(HTTPStatus.BAD_REQUEST, 'image field is required')
    rel_path = get_image_path(camera, '.jpg')
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)

    base_dir, _ = os.path.split(abs_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    with open(abs_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    camera.image_iter = (camera.image_iter + 1) % CAMERA_ITER_CIRCLE_SIZE
    camera.image = rel_path
    camera.last_image_update = timezone.now()
    camera.save(update_fields=['image', 'image_iter', 'last_image_update'])

    copy_to_static_place(abs_path, camera)

    return {}
