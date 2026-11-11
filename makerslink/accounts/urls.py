from django.urls import path, re_path, reverse_lazy
import django.contrib.auth.views as authViews

# User urls

urlpatterns = [
    path('login/', authViews.LoginView.as_view(template_name="accounts/login.html"),
         name="login"),
    path('logout/', authViews.LogoutView.as_view(template_name="accounts/logged_out.html"),
         name='logout',),
    path('password_reset/', authViews.PasswordResetView.as_view(template_name="accounts/password_reset.html",
                                                                email_template_name="accounts/password_reset_email.html",
                                                                subject_template_name="accounts/verification_subject.txt"), name='password_reset'),
    re_path(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
            authViews.PasswordResetConfirmView.as_view(template_name="accounts/set_password.html", success_url=reverse_lazy("password_reset_complete")), name='password_reset_confirm'),
    path('password_reset/done/', authViews.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"), name='password_reset_done'),
    path('password_reset/complete/', authViews.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"),
        name='password_reset_complete'),
]
