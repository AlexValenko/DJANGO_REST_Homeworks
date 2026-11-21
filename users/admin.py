from django.contrib import admin

from .models import Course, Lesson, Payment, User


@admin.register(Course)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "preview", "description", "created_at", "updated_at")


@admin.register(Lesson)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "course", "preview", "created_at", "link", "updated_at")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ("id", "email")
    exclude = ("password",)


admin.site.register(Payment)
