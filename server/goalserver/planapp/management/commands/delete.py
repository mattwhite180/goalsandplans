import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "deletes all data in db"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if settings.DEBUG:
            for u in User.objects.all():
                u.delete()
            self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
            self.stdout.write(self.style.SUCCESS("deleted all data"))
        else:
            self.stdout.write(self.style.FAILURE("cannot run delete on prod"))
