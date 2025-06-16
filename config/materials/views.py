from rest_framework import viewsets, mixins
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
