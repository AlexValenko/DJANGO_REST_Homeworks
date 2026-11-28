from urllib.parse import urlsplit

from rest_framework.serializers import ValidationError


def you_tube_only(value):
    """Валидатор, позволяет прикреплять ссылки только на PERMITTED_RESOURCE"""
    try:
        url = urlsplit(value)
        host = url.hostname
    except ValueError:
        raise ValidationError("Введите корректную ссылку") from None

    if url.scheme not in ("http", "https") or host not in ("youtube.com", "www.youtube.com"):
        raise ValidationError("Разрешены только ссылки на YouTube")
