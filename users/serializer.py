from rest_framework import serializers

from materials.models import Course
from materials.serializer import CourseSerializer, LessonSerializer

from .models import Payment, User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя. Здесь добавлены все поля потому что без поля password создание
    пользователя не срабатывает корректно, но при получении списка пользователей не нужно отображать все пароли"""

    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}


class UserOwnerSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных владельцу профиля"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "avatar",
            "user_city",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных любому авторизованному пользователю"""

    class Meta:
        model = User
        fields = ("email", "phone_number", "avatar", "user_city", "first_name", "is_active")


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "user", "pay_date", "course", "lesson", "pay_sum", "pay_method")

class PaymentCreateSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Payment
        fields = ("id", "course", "pay_sum", "pay_link")
        read_only_fields = ("id", "pay_sum", "pay_link")

class UserProfileSerializer(UserSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (*UserOwnerSerializer.Meta.fields, "payments")
        read_only_fields = ("is_staff", "is_active")
