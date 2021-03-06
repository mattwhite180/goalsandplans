import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from planapp.models import Goal, Plan, Task, TodoList, UserData


class Command(BaseCommand):
    help = "creates mock data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if settings.DEBUG:
            for g in Goal.objects.all():
                g.delete()
            for t in TodoList.objects.all():
                t.delete()
        usernameList = list()
        for u in User.objects.all():
            usernameList.append(u.username)
        if "root" in usernameList:
            root_user = User.objects.get(username="root")
        else:
            root_user = User.objects.create_user(
                username="root",
                password="asdf",
                is_superuser=True,
                is_staff=True
            )
            root_user.save()
            root_data = UserData.objects.create(user=root_user)
            root_data.save()
        if "test" in usernameList:
            test_user = User.objects.get(username="test")
        else:
            test_user = User.objects.create_user(
                username="test",
                password="asdf"
            )
            test_user.save()
            test_data = UserData.objects.create(user=test_user)
            test_data.save()
        g = Goal.objects.create(
            title="test goal",
            description="test goal description",
            user=root_user
        )
        g.save()
        todo1 = TodoList.objects.create(
            title="todolist A",
            description="description of todolist A",
            user=root_user
        )
        todo1.save()
        todo2 = TodoList.objects.create(
            title="todolist B",
            description="description of todolist B",
            user=root_user
        )
        todo2.save()
        p1 = Plan.objects.create(
            title="test plan (continuous)",
            description="this should increase the task count by 5",
            goal=g,
            continuous=True,
            limit=5,
            add_count=2,
            default_points=1,
            default_todolist=todo1,
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
        newp = Plan.objects.create(
            title="test plan (continuous) with diff tasks",
            description="this should increase the task count by 5",
            goal=g,
            continuous=True,
            limit=5,
            add_count=2,
            default_points=1,
            default_todolist=todo2,
            recurring_task_title="same task title",
            recurring_task_description="same task description",
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
        newp.save()
        newtt = Task.objects.create(
            title="diff task title",
            description="diff task descr",
            plan=newp,
            todolist=newp.default_todolist,
        )
        newtt.save()
        p2 = Plan.objects.create(
            title="test plan right side",
            description="not continuous",
            goal=g,
            continuous=False,
            limit=0,
            add_count=0,
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
        p2.save()
        t1 = Task.objects.create(
            title="test task", description="test description for task", plan=p2
        )
        t1.save()

        p3 = Plan.objects.create(
            title="test plan right side multiple",
            description="not continuous",
            goal=g,
            continuous=True,
            limit=3,
            add_count=3,
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
        p3.save()

        self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        self.stdout.write(self.style.SUCCESS("created test data"))
