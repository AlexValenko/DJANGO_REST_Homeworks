from rest_framework.serializers import ModelSerializer

from materials.models import Course


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "preview", "description",)
