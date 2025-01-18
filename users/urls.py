from django.urls import path

from users.views import UserViewSet

urlpatterns = [
    path("register/", UserViewSet.as_view({"post": "register"}), name="register"),
    path("login/", UserViewSet.as_view({"post": "login"}), name="login"),
    path(
        "change-password/",
        UserViewSet.as_view({"post": "change_password"}),
        name="change-password",
    ),
    path("me/", UserViewSet.as_view({"get": "me"}), name="me"),
    path("allow-access/<uuid:user_id>/", UserViewSet.as_view({"patch": "allow_user_access"}), name="allow-access"),
    path("get-all-users/", UserViewSet.as_view({"get": "get_all_users"}), name="get_all_users"),
    path("send-mail-reset-password/", UserViewSet.as_view({"patch": "reset_password_send_mail"}),
         name="send-mail-reset-password"),
    path("reset-password/", UserViewSet.as_view({"patch": "reset_password"}), name="reset-password"),
]
