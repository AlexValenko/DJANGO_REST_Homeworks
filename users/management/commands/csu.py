import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Создает суперпользователя"""
        user = User.objects.create(email=os.getenv("ADMIN_EMAIL"))
        user.set_password(os.getenv("ADMIN_PASS"))
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
