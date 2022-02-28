import datetime

from django.contrib.auth.models import AnonymousUser, User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Task, Issue
import time

class Command(BaseCommand):
    help = "creates tasks from plans"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        created = 0
        for plan in Plan.objects.filter(continuous=True):
            deltaDate = datetime.date.today() - plan.last_updated
            if (deltaDate.days >= 1 and plan.today()) or plan.keep_at_limit:
                try:
                    for i in range(plan.add_count):
                        currentCount = Task.objects.filter(plan=plan).count()
                        if currentCount < plan.limit:
                            newT = Task.objects.create(
                                title=plan.recurring_task_title,
                                description=plan.recurring_task_description,
                                priority=plan.default_priority,
                                plan=plan,
                                points=plan.default_points,
                            )
                            if plan.default_todolist:
                                newT.todolist = plan.default_todolist
                            newT.save()
                            created += 1
                    plan.last_updated = datetime.date.today()
                    plan.save()
                except Exception as e:
                    i = Issue.objects.create(
                        obj_info = "Plan: " + str(plan.id),
                        where = "taskify",
                        exception_string = str(e)
                    )
                    i.save()
        self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        self.stdout.write(
            self.style.SUCCESS('Successfully created "%s" tasks\n----' % created)
        )