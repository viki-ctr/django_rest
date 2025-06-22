from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscription, Course
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model


User = get_user_model()


@shared_task
def send_course_update_notification(course_id):
    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course)

    for subscription in subscriptions:
        send_mail(
            f'Обновление курса {course.title}',
            'В курсе появились новые материалы.',
            settings.EMAIL_HOST_USER,
            [subscription.user.email],
            fail_silently=False,
        )


@shared_task
def check_inactive_users():
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    for user in inactive_users:
        user.is_active = False
        user.save()
