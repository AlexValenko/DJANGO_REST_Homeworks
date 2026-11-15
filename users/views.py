from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Payment, User
from .permission import IsOwner, IsOwnProfile
from .serializer import PaymentSerializer, UserProfileSerializer, UserRegisterSerializer, UserSerializer


class UserCreateAPIView(CreateAPIView):
    """Эндпоинт для создания пользователя"""

    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Переопределяет метод создания пользователя, чтобы избежать конфликта из-за username = None"""
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserListApiView(ListAPIView):
    """Отображение списка пользователей - для любого авторизованного пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveApiView(RetrieveAPIView):
    """Отображение профиля пользователя - полные данные для владельца, общие данные - для любого авторизованного."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return UserProfileSerializer
        return UserSerializer


class UserUpdateApiView(UpdateAPIView):
    """Позволяет редактировать данные пользователя только владельцу."""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnProfile]


class UserDestroyApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnProfile]

    def destroy(self, request, *args, **kwargs):
        """Запрещает удалять пользователя с платежами"""
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Нельзя удалить пользователя, у которого есть платежи."},
                status=status.HTTP_409_CONFLICT,
            )


class PaymentList(ListAPIView):
    """Возвращает список платежей с возможностью фильтрации и сортировки
    пример запроса по сортировке ...//users/payments/?ordering=-pay_date
    пример запроса фильтрация по курсу/users/payments/?course=1 (по уроку также, ?lesson=1)
    пример запроса с фильтрацией по типу оплаты/users/payments/?pay_method=cash
    пример запроса с фильтрацией и сортировкой /users/payments/?pay_method=transaction&ordering=-pay_date
    Просмотр платежей только владельцу
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = (
        "course",
        "lesson",
        "pay_method",
    )
    ordering_fields = ("pay_date",)

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
