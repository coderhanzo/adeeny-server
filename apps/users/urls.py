from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("jwt/refresh/", views.refresh_token_view, name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path("jwt/create/", views.login_view, name="login"),
    path("users/", views.signup_view, name="register"),
    path("users/me/", views.get_logged_in_user, name="get_logged_in"),
    path("users/logout/", views.logout, name="logout"),
    path("users/reset_password/", views.SetPassword.as_view(), name="set_password"),
    path("users/all/", views.get_all_users, name="get_all_users"),
    path("password-reset/", views.custom_password_reset_view),
    path("password-reset-confirm/", views.SetPassword.as_view()),
    path("delete/<int:id>", views.delete_user, name="delete_user"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    # path("users/filter/", views.GetUsersPerRole.as_view(), name="create_superadmin"),
]

"""
password reset isn't working - it can't find the user logged in
get logged in user too doesn't seem to work - no error message provided or displayed
"""