import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Goal(models.Model):

    class PriorityLevels(models.TextChoices):
        BACKLOG = 'BK', _('Backlog')
        LOW = 'LW', _('Low')
        MEDIUM = 'MD', _('Medium')
        HIGH = 'HI', _('High')
        UG = 'UG', _('Urgent')

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    finished = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=2,
        choices=PriorityLevels.choices,
        default=PriorityLevels.LOW,
    )
    cost = models.IntegerField(default=0)
    done_tasks = models.IntegerField(default=0)
    total_tasks = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def pull_report(self, *args, **kwargs):
        total = 0
        done = 0
        for p in Plan.objects.filter(goal=self):
            for t in Task.objects.filter(plan=p):
                total += 1
                if t.finished:
                    done += 1
        d = dict()
        d['t'] = total
        d['d'] = done
        return d

class Plan(models.Model):

    class PriorityLevels(models.TextChoices):
        BACKLOG = 'BK', _('Backlog')
        LOW = 'LW', _('Low')
        MEDIUM = 'MD', _('Medium')
        HIGH = 'HI', _('High')
        UG = 'UG', _('Urgent')

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    continuous = models.BooleanField(default=False)
    limit = models.IntegerField(default=10)
    add_count = models.IntegerField(default=1)
    default_priority = models.CharField(
        max_length=2,
        choices=PriorityLevels.choices,
        default=PriorityLevels.LOW,
    )
    last_updated = models.DateField('last_updated', default=timezone.now() - timezone.timedelta(days=1))
    add_period = models.IntegerField(default=1)
    recurring_task_title = models.CharField(max_length=200, default='')
    recurring_task_description = models.CharField(max_length=2000, default='')

class Task(models.Model):

    class PriorityLevels(models.TextChoices):
        BACKLOG = 'BK', _('Backlog')
        LOW = 'LW', _('Low')
        MEDIUM = 'MD', _('Medium')
        HIGH = 'HI', _('High')
        UG = 'UG', _('Urgent')

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    due = models.DateField("due_date")
    finished = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=2,
        choices=PriorityLevels.choices,
        default=PriorityLevels.LOW,
    )
    cost = models.IntegerField(default=1)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def is_due_soon(self):
        return self.due < timezone.now() + datetime.timedelta(days=2)