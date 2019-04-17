from django.conf import settings

def extra_menu_processor(request):
    extra = {}
    if hasattr(settings, "MENU_TITLE"):
    	extra['menu_title'] = settings.MENU_TITLE
    if hasattr(settings, "LOGO"):
        extra['logo'] = settings.LOGO
    if hasattr(settings, "MENU_EXTRA"):
        extra['menu_extra'] = settings.MENU_EXTRA
    
    return extra
