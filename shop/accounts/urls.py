from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("sign-up/", views.register, name="sign-up"),
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/change-profile/", views.change_profile, name="change-profile"),
    path("profile/change-password/",
         views.UpdatePassword.as_view(), name="password-change"),
]
