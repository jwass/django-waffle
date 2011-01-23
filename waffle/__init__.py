from decimal import Decimal
import random

from django.conf import settings

from waffles.models import Flag


def is_active(request, flag_name):
    try:
        flag = Flag.objects.get(name=flag_name)
    except Flag.DoesNotExist:
        return getattr(settings, 'WAFFLE_DEFAULT', False)

    if getattr(settings, 'WAFFLE_OVERRIDE', False):
        if flag_name in request.GET:
            return True

    if flag.everyone:
        return True
    elif flag.everyone == False:
        return False

    user = request.user

    if flag.authenticated and user.is_authenticated():
        return True

    if flag.staff and user.is_staff:
        return True

    if flag.superusers and user.is_superuser:
        return True

    if user in flag.users.all():
        return True

    for group in flag.groups.all():
        if group in user.groups.all():
            return True

    if flag.percent > 0:
        if not hasattr(request, 'waffles'):
            request.waffles = {}
        request.waffles[flag_name] = False

        format = getattr(settings, 'WAFFLE_COOKIE', 'dwf_%s')
        cookie = format % flag_name
        if cookie in request.COOKIES:
            request.waffles[flag_name] = (request.COOKIES[cookie] == 'True')
            return request.waffles[flag_name]

        rand = Decimal(random.randint(0, 999)) / 10
        if rand <= flag.percent:
            request.waffles[flag_name] = True
            return True

    return False