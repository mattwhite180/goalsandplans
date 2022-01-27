import datetime

from django.contrib.auth.models import AnonymousUser, User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Task


class Command(BaseCommand):
    help = "changes existing tasks to match plan"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            for p in Plan.objects.filter(continuous=True):
                for t in Task.objects.filter(plan=p).filter(title=p.recurring_task_title):
                    t.description = p.recurring_task_description
                    t.points = p.default_points
                    t.todolist = p.default_todolist
                    t.priority = p.default_priority
                    t.save()
        except:
            raise CommandError("error running planify.py")
