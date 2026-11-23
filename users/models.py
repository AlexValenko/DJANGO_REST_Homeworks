from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CharField
from phonenumber_field.modelfields import PhoneNumberField

from materials.models import Course, Lesson


class User(AbstractUser):
    """Класс описания пользователей сайта"""

    username = None
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Укажите электронную почту")
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name="Телефон",
        region="RU",
        help_text="Введите свой номер телефона (необязательно)",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        null=True,
        blank=True,
        verbose_name="Изображение",
        help_text="Загрузите изображение (необязательно)",
    )
    user_city = CharField(max_length=150, blank=True, null=True, verbose_name="Город", help_text="Введите ваш город")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAY_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transaction", "Перевод на счет"),
        ("stripe", "Онлайн оплата через Stripe"),
    ]

    user = models.ForeignKey(to=User, related_name="payments", on_delete=models.PROTECT, verbose_name="Пользователь")
    pay_date = models.DateTimeField(verbose_name="дата оплаты", help_text="Дата и время оплаты", blank=True, null=True)
    course = models.ForeignKey(
        to=Course, related_name="payments", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Курс"
    )
    lesson = models.ForeignKey(
        to=Lesson, related_name="payments", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Урок"
    )
    pay_sum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        help_text="Введите сумму оплаты",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    pay_method = models.CharField(
        max_length=12, verbose_name="Метод оплаты", help_text="Выберите метод оплаты", choices=PAY_METHOD_CHOICES
    )
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии", help_text="Укажите ID сессии"
    )
    pay_link = models.URLField(
        max_length=2048, blank=True, null=True, verbose_name="Ссылка на оплату", help_text="Укажите ссылку на оплату"
    )

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self):
        return f"Оплата №{self.pk} — {self.pay_sum}"


class Subscription(models.Model):
    """Класс, описывающий наличие подписки у пользователя на курс"""

    user = models.ForeignKey(
        to=User, related_name="subscription", on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    course = models.ForeignKey(to=Course, related_name="subscription", on_delete=models.CASCADE, verbose_name="Курс")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_subscription_user_course",
            ),
        ]
