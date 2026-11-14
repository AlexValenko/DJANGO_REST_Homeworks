from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "preview",
            "description",
        )


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "name",
            "description",
            "course",
            "preview",
            "link",
        )


class CourseWithLessonsSerializer(ModelSerializer):
    lessons_counts = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    @staticmethod
    def get_lessons_counts(course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = ("id", "name", "preview", "description", "lessons_counts", "lessons")
