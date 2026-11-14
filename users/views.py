from django.db.models.deletion import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response

from .models import Payment, User
from .serializer import PaymentSerializer, UserProfileSerializer, UserSerializer


class UserListApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveApiView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDestroyApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
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
