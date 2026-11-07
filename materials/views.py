from rest_framework import viewsets
from .models import Course
from materials.serializer import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

