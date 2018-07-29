from django.urls import path, re_path
from django.conf.urls import url
from .views import RegistrationView
import django.contrib.auth.views
from . import views

# User urls

urlpatterns = [
    path('login/', django.contrib.auth.views.login,
        {'template_name': 'accounts/login.html'}, name='login'),
    path('logout/', django.contrib.auth.views.logout,
        {'template_name': 'accounts/logged_out.html'}, name='logout',),
    path('register/', RegistrationView.as_view(), name='register'),
    path('register/done/', django.contrib.auth.views.password_reset_done,
        {'template_name': 'accounts/register_done.html',}, name='register-done'),
    re_path(r'^register/password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        django.contrib.auth.views.password_reset_confirm,{
            'template_name': 'accounts/register_set_password.html',
            'post_reset_redirect': 'register-complete',
        }, name='password_set_confirm'),
    path('register/complete/', django.contrib.auth.views.password_reset_complete, {
        'template_name': 'accounts/register_complete.html',
    }, name='register-complete'),
]

