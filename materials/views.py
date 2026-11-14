from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from materials.serializer import CourseSerializer, CourseWithLessonsSerializer, LessonSerializer
from users.permission import IsModer

from .models import Course, Lesson


class CourseViewSet(viewsets.ModelViewSet):

    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseWithLessonsSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            self.permission_classes = (
                IsAuthenticated,
                ~IsModer,
            )
        elif self.action in ["update", "partial_update", "retrieve"]:
            self.permission_classes = (
                IsAuthenticated,
                IsModer,
            )
        return super().get_permissions()


class LessonCreateApiView(CreateAPIView):
    """Контроллер для создания уроков. Только для авторизованных и НЕ модераторов"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]


class LessonListApiView(ListAPIView):
    """Контроллер для просмотра списка уроков. Только для авторизованных (настройки по умолчанию)"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveApiView(RetrieveAPIView):
    """Контроллер для просмотра деталей уроков. Только для модераторов"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [
        IsModer,
    ]


class LessonUpdateApiView(UpdateAPIView):
    """Контроллер для обновления данных уроков. Только для модераторов"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [
        IsModer,
    ]


class LessonDestroyApiView(DestroyAPIView):
    """Контроллер для обновления уладения уроков. Только для авторизованных и НЕ модераторов"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]
