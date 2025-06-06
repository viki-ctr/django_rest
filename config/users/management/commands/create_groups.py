from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates moderator group if not exists'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа модераторов создана'))
        else:
            self.stdout.write('Группа модераторов уже существует')
