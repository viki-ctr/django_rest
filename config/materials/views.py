from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModerator, IsOwner
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Subscription
from .paginators import LessonPaginator, CoursePaginator
from drf_spectacular.utils import extend_schema
from django.urls import reverse
from .services.stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
    get_stripe_session_status
)
from users.models import Payment


class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = CoursePaginator
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'retrieve', 'list']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['create', 'destroy']:
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if not self.request.user.groups.filter(name='moderators').exists():
            return Course.objects.filter(owner=self.request.user)
        return Course.objects.all()


class LessonViewSet(viewsets.ModelViewSet):
    pagination_class = LessonPaginator
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'retrieve', 'list']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['create', 'destroy']:
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if not self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.filter(owner=self.request.user)
        return Lesson.objects.all()


@extend_schema(
    description='Управление подписками на курсы',
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'course_id': {'type': 'integer', 'description': 'ID курса'}
                }
            }
        }
    },
    responses={
        200: {
            'description': 'Результат операции с подпиской',
            'content': {
                'application/json': {
                    'example': {'message': 'Подписка добавлена/удалена'}
                }
            }
        }
    }
)
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course
        )

        if not created:
            subscription.delete()
            message = 'Подписка удалена'
        else:
            message = 'Подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)


@extend_schema(
    description='Создание платежной сессии для курса',
    responses={
        201: {
            'description': 'Ссылка для оплаты',
            'content': {
                'application/json': {
                    'example': {
                        'payment_link': 'https://checkout.stripe.com/pay/...',
                        'payment_id': 1
                    }
                }
            }
        }
    }
)
class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        product = create_stripe_product(
            name=course.title,
            description=course.description
        )

        price = create_stripe_price(
            product_id=product.id,
            amount=1000
        )

        success_url = request.build_absolute_uri(reverse('payment-success'))
        cancel_url = request.build_absolute_uri(reverse('payment-cancel'))
        session = create_stripe_checkout_session(
            price_id=price.id,
            success_url=success_url,
            cancel_url=cancel_url
        )

        payment = Payment.objects.create(
            user=user,
            paid_course=course,
            amount=10.00,
            payment_method='transfer',
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_session_id=session.id,
            stripe_payment_link=session.url
        )

        return Response({
            'payment_link': session.url,
            'payment_id': payment.id
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    description='Проверка статуса платежа',
    responses={
        200: {
            'description': 'Статус платежа',
            'content': {
                'application/json': {
                    'example': {
                        'status': 'paid',
                        'payment_id': 1,
                        'course_id': 1
                    }
                }
            }
        }
    }
)
class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        status = get_stripe_session_status(payment.stripe_session_id)

        return Response({
            'status': status,
            'payment_id': payment.id,
            'course_id': payment.paid_course.id
        })
