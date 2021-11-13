import datetime

from django.db import models
from django.utils import timezone

class Goal(models.Model):

    class PriorityLevels(models.IntegerChoices):
        BACKLOG = 1
        LOW = 2
        MEDIUM = 3
        HIGH = 4
        URGENT = 5

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    created_on = models.DateTimeField('created on', default=timezone.now())
    due = models.DateTimeField("due_date")
    finished = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PriorityLevels.choices)
    cost = models.IntegerField(default=1)
    done_tasks = models.IntegerField(default=1)
    total_tasks = models.IntegerField(default=1)

    def pull_report(self, *args, **kwargs):
        total = 0
        done = 0
        for p in Plan.objects.filter(goal=self):
            for t in Task.objects.filter(plan=p):
                if t.active:
                    total += 1
                    if t.finished:
                        done += 1
        d = dict()
        d['t'] = total
        d['d'] = done
        return d

class Plan(models.Model):

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    count_inactive = models.BooleanField(default=True)
    continuous = models.BooleanField(default=False)
    limit = models.IntegerField(default=10)
    add_count = models.IntegerField(default=1)
    add_per_hour = models.IntegerField(default=24)
    recurring_task_title = models.CharField(max_length=200, default='')
    recurring_task_description = models.CharField(max_length=2000, default='')

class Task(models.Model):

    class PriorityLevels(models.IntegerChoices):
        BACKLOG = 1
        LOW = 2
        MEDIUM = 3
        HIGH = 4
        URGENT = 5

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    created_on = models.DateTimeField('created on', default=timezone.now())
    due = models.DateTimeField("due_date")
    finished = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PriorityLevels.choices)
    cost = models.IntegerField(default=1)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def is_due_soon(self):
        return self.due < timezone.now() + datetime.timedelta(days=2)