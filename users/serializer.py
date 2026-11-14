from rest_framework import serializers

from .models import Payment, User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя. Здесь добавлены все поля потому что без поля password создание
    пользователя не срабатывает корректно, но при получении списка пользователей не нужно отображать все пароли"""
    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone_number", "avatar", "user_city", "first_name", "last_name", "is_active")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "user", "pay_date", "course", "lesson", "pay_sum", "pay_method")


class UserProfileSerializer(UserSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, "payments")
