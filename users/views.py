from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView,
                                     get_object_or_404)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course

from .models import Payment, Subscription, User
from .permission import IsOwnProfile
from .serializer import (PaymentCreateSerializer, PaymentSerializer, UserProfileSerializer, UserRegisterSerializer,
                         UserSerializer)
from .services import create_stripe_price, create_stripe_sessions, get_payment_status


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
        if getattr(self, "swagger_fake_view", False):
            return UserSerializer
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


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course"],
            properties={"course": openapi.Schema(type=openapi.TYPE_INTEGER)},
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        # получаем пользователя из self.requests
        user = self.request.user
        # получаем id курса из self.reqests.data
        course_id = self.request.data.get("course")
        # получаем объект курса из базы
        course = get_object_or_404(Course, pk=course_id)
        # получаем объекты подписок по текущему пользователю и курса
        subscriptions = Subscription.objects.filter(user=user, course=course)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subscriptions.exists():
            subscriptions.delete()
            message = "подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"
        # Возвращаем ответ в API
        return Response({"message": message})


class PaymentCreateAPIView(CreateAPIView):
    """Создание оплаты"""

    serializer_class = PaymentCreateSerializer
    queryset = Payment.objects.all()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        amount = course.price
        if amount is None or amount <= 0:
            raise ValidationError({"course": "У курса должна быть задана положительная цена."})

        price = create_stripe_price(amount, course.name)
        session_id, payment_link = create_stripe_sessions(price)

        serializer.save(
            user=self.request.user,
            pay_sum=amount,
            pay_method="stripe",
            session_id=session_id,
            pay_link=payment_link,
        )


class PaymentRetrieveAPIView(APIView):
    """Класс для отображения статуса оплаты. Если тип оплаты - stripe - запрашивает статус платежа по номеру сессии,
    в stripe через сервисную функцию get_payment_status, сохраняет значение в БД, если paid, то сохраняет дату оплаты
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_status": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            404: "Платёж не найден",
        },
    )
    def get(self, request, pk):
        payment = get_object_or_404(
            Payment,
            pk=pk,
            user=request.user,
            pay_method="stripe",
        )
        if not payment.session_id:
            raise ValidationError({"detail": "У платежа нет сессии Stripe."})

        payment_status = get_payment_status(payment.session_id)
        payment.pay_status = payment_status
        fields_to_update = ["pay_status"]

        if payment_status == "paid" and payment.pay_date is None:
            payment.pay_date = timezone.now()
            fields_to_update.append("pay_date")

        payment.save(update_fields=fields_to_update)
        return Response({"payment_status": payment_status})
