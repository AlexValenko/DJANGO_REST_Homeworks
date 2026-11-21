from rest_framework import serializers

from materials.models import Course, Lesson
from materials.validators import you_tube_only


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "preview",
            "description",
            "owner",
        )
        read_only_fields = ("owner",)


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения уроков"""
    link = serializers.CharField(validators=[you_tube_only])

    class Meta:
        model = Lesson
        fields = (
            "id",
            "name",
            "description",
            "course",
            "preview",
            "link",
            "owner",
        )
        read_only_fields = ("owner",)



class CourseWithLessonsSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()

    def get_visible_lessons(self, course):
        user = self.context["request"].user
        if user.groups.filter(name="moders").exists():
            return course.lessons.all()
        return course.lessons.filter(owner=user)

    def get_lessons(self, course):
        lessons = self.get_visible_lessons(course)
        return LessonSerializer(lessons, many=True, context=self.context).data

    def get_lessons_count(self, course):
        return self.get_visible_lessons(course).count()

    class Meta:
        model = Course
        fields = ("id", "name", "preview", "description", "lessons_count", "lessons")
