from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import AnonymousUser, User
from django.conf import settings
from planapp.models import Goal, Plan, Task
import datetime


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
        if "test" in usernameList:
            test_user = User.objects.get(username="test")
        else:
            test_user = User.objects.create_user(username="test", password="1234")
            test_user.save()
        if "mattw" in usernameList:
            mattw = User.objects.get(username="mattw")
        else:
            mattw = User.objects.create_user(username="mattw", password="mw")
            mattw.save()
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
            add_count=5,
            add_period=1,
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        p1.save()
        p2 = Plan.objects.create(
            title="test plan (not continuous)",
            description="this should not increase the task count",
            goal=g,
            continuous=False,
            limit=700,
            add_count=700,
            add_period=1,
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        p2.save()
        p3 = Plan.objects.create(
            title="test plan (continuous outside of time)",
            description="this should not increase the task count",
            goal=g,
            continuous=True,
            limit=20000,
            add_count=20000,
            add_period=2,
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        p3.save()
        p = Plan.objects.create(
            title="test plan (continuous near limit)",
            description="this should only increase the task count by 18",
            goal=g,
            continuous=True,
            limit=20,
            add_count=20,
            add_period=1,
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        p.save()
        t1 = Task.objects.create(
            title="task test1",
            description="see if last plan will go over the limit",
            plan=p,
        )
        t1.save()
        t2 = Task.objects.create(
            title="task test2",
            description="see if last plan will go over the limit",
            plan=p,
        )
        t2.save()
        mg1 = Goal.objects.create(
            title="first goal",
            description="first goal description",
            priority=Goal.priority.field.choices[3][0],
            user=mattw,
        )
        mg2 = Goal.objects.create(
            title="second goal",
            description="second goal description",
            priority=Goal.priority.field.choices[3][0],
            user=mattw,
        )
        mg2.save()
        pp1 = Plan.objects.create(
            title="continuous plan of second goal",
            description="task associated with second goal. ",
            goal=mg2,
            continuous=True,
            limit=10,
            add_count=3,
            add_period=1,
            default_priority=Goal.priority.field.choices[2][0],
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        pp1.save()
        mp1 = Plan.objects.create(
            title="continuous plan of first goal",
            description="plan associated with first goal. ",
            goal=mg1,
            continuous=True,
            limit=10,
            add_count=3,
            add_period=1,
            default_priority=Goal.priority.field.choices[3][0],
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        mp1.save()
        mp2 = Plan.objects.create(
            title="non-continuous plan of first goal",
            description="plan associated with first goal. ",
            goal=mg1,
            continuous=False,
            limit=10,
            add_count=3,
            add_period=1,
            default_priority=Goal.priority.field.choices[2][0],
            recurring_task_title="task title goes here",
            recurring_task_description="task description goes here",
        )
        mp2.save()
        mt1 = Task.objects.create(
            title="task2",
            description="test task 2",
            plan=mp1,
            priority=Goal.priority.field.choices[0][0],
        )
        mt1.save()
        mt2 = Task.objects.create(
            title="task1",
            description="test task 1",
            plan=mp1,
            priority=Goal.priority.field.choices[4][0],
        )
        mt2.save()

        self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        self.stdout.write(self.style.SUCCESS("created test data"))
