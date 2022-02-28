import datetime

from django.contrib.auth.models import AnonymousUser, User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Task, Issue
from django.core.management import call_command
from planapp.models import Issue


import time

class Command(BaseCommand):
    help = "creates tasks from plans"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            WAIT_TIME = 1 * 60 * 5
            while True:
                call_command("taskify")
                time.sleep(WAIT_TIME)
        except Exception as e:
            i = Issue.objects.create(
                obj_info = "crontask: outside of taskify"
                where = "crontask",
                exception_string = str(e)
            )
            i.save()
