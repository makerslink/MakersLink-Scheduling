"""makerslink URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls import url

#Force using django server to server static even in prod. Not recommended, but
#this is such a small deployment.
if not settings.DEBUG:
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('scheduler/', include('scheduler.urls')),
    path('accounts/', include('accounts.urls')),
]

#Add URL maps to redirect the base URL to our application
# Denna skall bort sedan när det finns mer innehåll
from django.views.generic import RedirectView
urlpatterns += [
    path('', RedirectView.as_view(url='/scheduler/')),
]
