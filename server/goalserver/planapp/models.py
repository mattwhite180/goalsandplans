import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Goal(models.Model):

    class PriorityLevels(models.TextChoices):
        BACKLOG = '0 BK', _('Backlog')
        LOW = '1 LW', _('Low')
        MEDIUM = '2 MD', _('Medium')
        HIGH = '3 HI', _('High')
        UG = '4 UG', _('Urgent')

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    priority = models.CharField(
        max_length=4,
        choices=PriorityLevels.choices,
        default=PriorityLevels.LOW,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def pull_report(self, *args, **kwargs):
        total = 0
        for p in Plan.objects.filter(goal=self):
            for t in Task.objects.filter(plan=p):
                total += 1
        return total

class Plan(models.Model):

    class PriorityLevels(models.TextChoices):
        BACKLOG = '0 BK', _('Backlog')
        LOW = '1 LW', _('Low')
        MEDIUM = '2 MD', _('Medium')
        HIGH = '3 HI', _('High')
        UG = '4 UG', _('Urgent')

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    continuous = models.BooleanField(default=True)
    limit = models.IntegerField(default=10)
    add_count = models.IntegerField(default=1)
    default_priority = models.CharField(
        max_length=4,
        choices=PriorityLevels.choices,
        default=PriorityLevels.LOW,
    )
    last_updated = models.DateField('last_updated', default=datetime.date.today() - datetime.timedelta(hours=24))
    add_period = models.IntegerField(default=1)
    recurring_task_title = models.CharField(max_length=200, default='')
    recurring_task_description = models.CharField(max_length=2000, default='')

class Task(models.Model):

    class PriorityLevels(models.TextChoices):
        BACKLOG = '0 BK', _('Backlog')
        LOW = '1 LW', _('Low')
        MEDIUM = '2 MD', _('Medium')
        HIGH = '3 HI', _('High')
        UG = '4 UG', _('Urgent')

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    priority = models.CharField(
        max_length=4,
        choices=PriorityLevels.choices,
        default=PriorityLevels.LOW,
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def is_due_soon(self):
        return self.due < timezone.now() + datetime.timedelta(days=2)