from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'video_link': {'validators': [validate_youtube_url]}
        }


class CourseSerializer(serializers.ModelSerializer):

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons']

    def get_lessons_count(self, obj):
        return obj.lessons.count()
