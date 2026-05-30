from http import HTTPStatus

from ninja import Router
from ninja.errors import HttpError

from chat.presenters.refill import present_provider
from main.models.provider import Provider

router = Router(tags=['info'])


@router.get('/legal_info')
def show_legal_info(request):
    try:
        # Capture id for provider
        provider: Provider = Provider.objects.get(id=1)
    except Provider.DoesNotExist as provider_err:
        raise HttpError(HTTPStatus.NOT_FOUND, 'Провайдер не найден') from provider_err

    return present_provider(provider)
