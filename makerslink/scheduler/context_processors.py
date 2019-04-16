from django.conf import settings

def extra_menu_processor(request):
    if settings.MENU_EXTRA:
        return {'menu_extra': settings.MENU_EXTRA}
    else:
        return
