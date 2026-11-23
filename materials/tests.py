from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import User


class LessonsAPITestCase(APITestCase):
    """Класс тестов для проверки CRUD уроков."""

    def setUp(self):
        """Подготовка перед запуском каждого теста"""
        self.user = User.objects.create(email="user@user.com")
        self.second_user = User.objects.create(email="second_user@user.com")
        self.course = Course.objects.create(
            name="Тестовый курс", description="Тестовый курс описание", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Тестовый урок", description="Тестовый урок", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        """Тестирование просмотра одного экземпляра урока"""
        url = reverse("materials:lessons_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)
        self.assertEqual(data.get("course"), self.lesson.course.pk)

    def test_lesson_retrieve_by_second_user(self):
        """Тестирование просмотра одного экземпляра урока другим пользователем"""
        self.client.force_authenticate(user=self.second_user)
        url = reverse("materials:lessons_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_create(self):
        """Тестирвоание создания урока"""
        url = reverse("materials:lessons_create")
        data = {
            "name": "Создаваемый урок",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        """Тестирование изменения одного экземпляра урока"""
        url = reverse("materials:lessons_update", args=(self.lesson.pk,))
        updated_data = {
            "name": "Изменяемый урок урок",
        }
        response = self.client.patch(url, updated_data)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), "Изменяемый урок урок")
        self.assertEqual(data.get("course"), self.lesson.course.pk)

    def test_lesson_update_by_second_user(self):
        """Тестирование изменения чужого урока другим обычным пользователем"""
        self.client.force_authenticate(user=self.second_user)
        url = reverse("materials:lessons_update", args=(self.lesson.pk,))
        updated_data = {"name": "Изменить название"}
        response = self.client.patch(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Название не изменилось?
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Тестовый урок")

    def test_lesson_delete(self):
        """Тестирование удаления экземпляра урока"""
        url = reverse("materials:lessons_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_delete_by_second_user(self):
        """Тестирование удаления экземпляра чужого урока"""
        self.client.force_authenticate(user=self.second_user)
        url = reverse("materials:lessons_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Урок должен остаться в базе
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_lesson_list(self):
        """Тестирование просмотра списка уроков"""
        url = reverse("materials:lessons_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": self.lesson.pk,
                        "name": self.lesson.name,
                        "description": self.lesson.description,
                        "course": self.lesson.course.pk,
                        "preview": None,
                        "link": None,
                        "owner": self.lesson.owner.pk,
                    }
                ],
            },
        )

    def test_lesson_list_by_second_user(self):
        """Тестирование просмотра списка уроков вторым пользователем, у которого нет своих уроков"""
        self.client.force_authenticate(user=self.second_user)
        url = reverse("materials:lessons_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Список уроков пришел пустой
        self.assertEqual(
            response.json(),
            {"count": 0, "next": None, "previous": None, "results": []},
        )

    def test_moderator_can_not_create_lesson(self):
        """Тестирование, что модератор не создать свой урок."""
        moderator = User.objects.create(email="moderator@example.com")
        group, _ = Group.objects.get_or_create(name="moders")
        moderator.groups.add(group)
        self.client.force_authenticate(user=moderator)
        url = reverse("materials:lessons_create")
        data = {
            "name": "Урок от модератора",
            "link": "https://www.youtube.com/watch?12345",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Количество уроков осталось 1
        self.assertEqual(Lesson.objects.all().count(), 1)

    def test_moderator_can_update_lesson(self):
        """Тестирование, что модератор может изменять чужой урок."""
        moderator = User.objects.create(email="moderator@example.com")
        group, _ = Group.objects.get_or_create(name="moders")
        moderator.groups.add(group)
        self.client.force_authenticate(user=moderator)

        url = reverse("materials:lessons_update", args=(self.lesson.pk,))
        response = self.client.patch(url, {"name": "Обновлённый урок"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Обновлённый урок")

    def test_moderator_can_view_lessons_list(self):
        """Тестирование, что модератор может видеть уроки, не свои"""
        moderator = User.objects.create(email="moderator@example.com")
        group, _ = Group.objects.get_or_create(name="moders")
        moderator.groups.add(group)
        self.client.force_authenticate(user=moderator)

        url = reverse("materials:lessons_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": self.lesson.pk,
                        "name": self.lesson.name,
                        "description": self.lesson.description,
                        "course": self.lesson.course.pk,
                        "preview": None,
                        "link": None,
                        "owner": self.lesson.owner.pk,
                    }
                ],
            },
        )

    def test_moderator_can_not_delete_lesson(self):
        """Тестирование, что модератор не может удалить чужой урок."""
        moderator = User.objects.create(email="moderator@example.com")
        group, _ = Group.objects.get_or_create(name="moders")
        moderator.groups.add(group)
        self.client.force_authenticate(user=moderator)

        url = reverse("materials:lessons_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_create_lesson_invalid_link(self):
        """Тестирование с проверкой валидности ссылки на урок (только youtube)"""
        url = reverse("materials:lessons_create")
        data = {
            "name": "Создаваемый урок",
            "link": "https://vk.ru/clip-238117828_456239142",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Lesson.objects.all().count(), 1)
        self.assertEqual(
            response.json()["link"],
            ["Разрешены только ссылки на YouTube"],
        )


class NoneAuthAPITestCase(APITestCase):
    """Тест-кейс для неавторизованного пользователя"""

    def test_create_lesson(self):
        """Попытка создания урока без авторизации"""
        url = reverse("materials:lessons_create")
        data = {
            "name": "Создаваемый урок",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lessons_list(self):
        """Попытка просмотра списка уроков без авторизации"""
        url = reverse("materials:lessons_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lesson(self):
        """Попытка просмотра списка уроков без авторизации"""
        self.lesson = Lesson.objects.create(name="Тестовый урок")
        url = reverse("materials:lessons_retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_lesson(self):
        """Попытка редактирования урока без авторизации"""
        self.lesson = Lesson.objects.create(name="Тестовый урок")
        url = reverse("materials:lessons_update", args=(self.lesson.pk,))
        data = {"name": "Change name"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_lesson(self):
        """Попытка удаления урока без авторизации"""
        self.lesson = Lesson.objects.create(name="Тестовый урок")
        url = reverse("materials:lessons_delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
