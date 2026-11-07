from django.urls import path

from users.apps import UsersConfig
from users.views import UserDestroyApiView, UserListApiView, UserRetrieveApiView, UserUpdateApiView

app_name = UsersConfig.name

urlpatterns = [
    path("", UserListApiView.as_view(), name="users_list"),
    # Закомментировал создание пользователя, т.к. нет метода создания пароля и по заданию создание юзера не требуется
    #     path("create/", UserCreateApiView.as_view(), name="users_create"),
    path("<int:pk>/", UserRetrieveApiView.as_view(), name="users_retrieve"),
    path("<int:pk>/update/", UserUpdateApiView.as_view(), name="users_update"),
    path("<int:pk>/delete/", UserDestroyApiView.as_view(), name="users_delete"),
]
