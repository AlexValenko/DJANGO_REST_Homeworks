from rest_framework.serializers import ValidationError

PERMITTED_RESOURCE = "youtube.com"


def you_tube_only(value):
    """Валидатор, позволяет прикреплять ссылки только на PERMITTED_RESOURCE"""
    if PERMITTED_RESOURCE not in value:
        raise ValidationError("Нельзя прикреплять ссылки на сторонние источники")
