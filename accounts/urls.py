from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", AccountRegister.as_view(), name="accountRegister"),
    path("login/", AccountLogin.as_view(), name="accountLogin"),
    path("logout/", accountLogout, name="accountLogout"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
    path("profile/<int:id>", profileView, name="profile"),
    path("profile/<int:id>/edit", ProfileEditView.as_view(), name="profileEdit"),
    path("profile/<int:id>/delete", profileDelete, name="profileDelete"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/passwordResetForm.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/passwordResetDone.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/passwordResetConfirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/passwordResetComplete.html"
        ),
        name="password_reset_complete",
    ),
]
