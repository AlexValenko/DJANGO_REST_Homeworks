from rest_framework import serializers

from .models import Payment, User


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
