from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from main.models.order import Order


def reports(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('/my_admin/login/?next=/report')
    orders = (
        Order.objects.filter(
            _delta_kw__gt=0.1,
        )
        .order_by('-finished_at')
        .all()
    )
    return render(request, 'report.html', {'orders': orders})
