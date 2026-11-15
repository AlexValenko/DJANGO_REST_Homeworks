from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """Проверяет состоит ли пользователь в группе модераторов moders."""

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsOwnProfile(BasePermission):
    """Разрешает пользователю редактировать свой профиль."""

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk
