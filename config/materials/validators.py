from django.core.exceptions import ValidationError
from urllib.parse import urlparse

def validate_youtube_url(value):
    if value:
        domain = urlparse(value).netloc
        if 'youtube.com' not in domain and 'youtu.be' not in domain:
            raise ValidationError('Разрешены только ссылки на YouTube')
