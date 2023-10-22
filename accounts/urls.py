from django.urls import path
from .views import *

urlpatterns = [
    path("register/", AccountRegister.as_view(), name="accountRegister"),
    path("login/", AccountLogin.as_view(), name="accountLogin"),
    path("logout/", accountLogout, name="accountLogout"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
]
