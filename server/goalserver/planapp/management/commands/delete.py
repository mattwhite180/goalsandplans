from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import AnonymousUser, User
from planapp.models import Goal, Plan, Task
import datetime

class Command(BaseCommand):
    help = 'deletes all data in db'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for u in User.objects.all():
            u.delete()

        self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        self.stdout.write(self.style.SUCCESS('deleted all data'))