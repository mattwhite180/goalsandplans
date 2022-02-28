import datetime

from django.contrib.auth.models import AnonymousUser, User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Task, Issue
from django.core.management import call_command

import time

class Command(BaseCommand):
    help = "creates tasks from plans"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        WAIT_TIME = 1 * 60 * 60
        while True:
            call_command("taskify")
            time.sleep(WAIT_TIME)
