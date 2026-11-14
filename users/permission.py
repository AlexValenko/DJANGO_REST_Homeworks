from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """Проверяет состоит ли пользователь в группе модераторов moders"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()
