from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (
    PaymentList,
    SubscriptionAPIView,
    UserCreateAPIView,
    UserDestroyApiView,
    UserListApiView,
    UserRetrieveApiView,
    UserUpdateApiView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("", UserListApiView.as_view(), name="users_list"),
    # Закомментировал создание пользователя, т.к. нет метода создания пароля и по заданию создание юзера не требуется
    #     path("create/", UserCreateApiView.as_view(), name="users_create"),
    path("<int:pk>/", UserRetrieveApiView.as_view(), name="users_retrieve"),
    path("<int:pk>/update/", UserUpdateApiView.as_view(), name="users_update"),
    path("<int:pk>/delete/", UserDestroyApiView.as_view(), name="users_delete"),
    # payment
    path("payments/", PaymentList.as_view(), name="payment_list"),
    # регистрация пользователей и авторизация JWT
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    # Создание/отклонение подписки пользователя на курс
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
]
