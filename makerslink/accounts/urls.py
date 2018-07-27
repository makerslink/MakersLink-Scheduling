from django.urls import path
from django.conf.urls import url
from .views import RegistrationView
import django.contrib.auth.views
from . import views

# User urls

urlpatterns += [
    url(r'^login/$', django.contrib.auth.views.login, {'template_name': 'registration/login.html'}, name='login',),
    url(r'^logout/$', django.contrib.auth.views.logout, {'template_name': 'registration/logged_out.html'}, name='logout',),
    url(r'^register/$', RegistrationView.as_view(), name='register'),
    url(r'^register/done/$', django.contrib.auth.views.password_reset_done, {
        'template_name': 'registration/initial_done.html',
    }, name='register-done'),
    url(r'^register/password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        django.contrib.auth.views.password_reset_confirm, {
            'template_name': 'registration/initial_confirm.html',
            'post_reset_redirect': 'register-complete',
        }, name='register-confirm'),
    url(r'^register/password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        django.contrib.auth.views.password_reset_confirm, {
            'template_name': 'registration/initial_confirm.html',
            'post_reset_redirect': 'register-complete',
        }, name='password_reset_confirm'),
    url(r'^register/complete/$', django.contrib.auth.views.password_reset_complete, {
        'template_name': 'registration/initial_complete.html',
    }, name='register-complete'),
]

