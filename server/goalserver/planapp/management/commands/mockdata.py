import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Prize, Task, TodoList, UserData


class Command(BaseCommand):
    help = "creates mock data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if settings.DEBUG:
            for g in Goal.objects.all():
                g.delete()
        usernameList = list()
        for u in User.objects.all():
            usernameList.append(u.username)
        if "root" in usernameList:
            root_user = User.objects.get(username="root")
        else:
            root_user = User.objects.create_user(
                username="root", password="asdf", is_superuser=True, is_staff=True
            )
            root_user.save()
            root_data = UserData.objects.create(user=root_user)
            root_data.save()
        if "test" in usernameList:
            test_user = User.objects.get(username="test")
        else:
            test_user = User.objects.create_user(username="test", password="asdf")
            test_user.save()
            test_data = UserData.objects.create(user=test_user)
            test_data.save()
        g = Goal.objects.create(
            title="test goal", description="test goal description", user=test_user
        )
        g.save()
        p1 = Plan.objects.create(
            title="test plan (continuous)",
            description="this should increase the task count by 5",
            goal=g,
            continuous=True,
            limit=5,
            add_count=2,
            default_points=1,
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
        p1.save()

        self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        self.stdout.write(self.style.SUCCESS("created test data"))
