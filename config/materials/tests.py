from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from materials.models import Course, Lesson, Subscription
from users.models import User
from django.core.management import call_command


class BaseTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('migrate')


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.moderators_group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator = User.objects.create(email='moderator@example.com')
        self.moderator.groups.add(self.moderators_group)

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user,
            video_link='https://youtube.com/test'
        )

    def test_lesson_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Lesson",
            "course": self.course.id,
            "video_link": "https://youtube.com/new"
        }
        response = self.client.post(
            '/api/lessons/',  # Используем прямой URL вместо reverse
            data=data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_lesson_update_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Updated Lesson"}
        response = self.client.patch(
            f'/api/lessons/{self.lesson.id}/',  # Прямой URL
            data=data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='user@example.com')
        self.course = Course.objects.create(title='Test Course')

    def test_subscription_create(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/subscriptions/',  # Прямой URL
            data={"course_id": self.course.id}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

    def test_subscription_delete(self):
        Subscription.objects.create(
            user=self.user,
            course=self.course
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/subscriptions/',  # Прямой URL
            data={"course_id": self.course.id}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )
