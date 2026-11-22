from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import Subscription, User


class SubscriptionAPITestCase(APITestCase):
    """Класс тестов для проверки работы подписки"""

    def setUp(self):
        """Подготовка перед запуском теста - создание объектов"""
        self.user = User.objects.create(email="user@user.com")
        self.course = Course.objects.create(
            name="Тестовый курс", description="Тестовый курс описание", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Тестовый урок", description="Тестовый урок", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        """ПРоверка, что по умолчанию подписка на курс не добавлена"""
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("is_subscribed"), False)

    def test_set_subscription(self):
        """Тестирование добавления подписки"""
        url = reverse("users:subscriptions")
        course_data = {"course": self.course.pk}
        response1 = self.client.post(url, course_data)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        result = response1.json()
        self.assertEqual(result, {"message": "подписка добавлена"})
        # ПРоверка что изменился статус подписки
        response2 = self.client.get(reverse("materials:course-detail", args=(self.course.pk,)))
        self.assertIs(response2.json()["is_subscribed"], True)

    def test_detach_subscription(self):
        """Тестирование удаления подписки"""
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("users:subscriptions")
        course_data = {"course": self.course.pk}
        response = self.client.post(url, course_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertEqual(result, {"message": "подписка удалена"})
        response2 = self.client.get(reverse("materials:course-detail", args=(self.course.pk,)))
        self.assertIs(response2.json()["is_subscribed"], False)
