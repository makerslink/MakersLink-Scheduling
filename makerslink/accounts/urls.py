from django.urls import path, re_path
from django.conf.urls import url
from .views import RegistrationView
import django.contrib.auth.views as authViews
from . import views

# User urls

urlpatterns = [
    path('login/', authViews.LoginView.as_view(template_name="accounts/login.html"),
        name="login"),
    path('logout/', authViews.LogoutView.as_view(template_name="accounts/logged_out.html"),
        name='logout',),
    path('register/', RegistrationView.as_view(), name='register'),
    path('register/done/', authViews.PasswordResetDoneView.as_view(template_name="accounts/register_done.html"), name='register-done'),
    re_path(r'^register/password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        authViews.PasswordResetConfirmView.as_view(template_name="accounts/register_set_password.html",
            success_url="register-complete"), name='password_set_confirm'),
    path('register/complete/', authViews.PasswordResetCompleteView.as_view(
        template_name="accounts/register_complete.html"),
        name='register-complete'),
]

