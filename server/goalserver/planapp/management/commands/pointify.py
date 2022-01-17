import datetime

from django.contrib.auth.models import AnonymousUser, User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Task


class Command(BaseCommand):
    help = "creates tasks from plans"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            for p in Plan.objects.filter(continuous=True):
                for t in Task.objects.filter(plan=p):
                    t.points = p.default_points
                    t.save()
        except:
            raise CommandError("error running pointify.py")

        # self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        # self.stdout.write(
        #     self.style.SUCCESS('Successfully created "%s" tasks\n----' % created)
        # )
