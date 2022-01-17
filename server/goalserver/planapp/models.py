import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def pull_report(self, *args, **kwargs):
        report = dict()
        report["goal_count"] = str(Goal.objects.filter(user=self.user).count())
        report["plan_count"] = str(Plan.objects.filter(goal__in=Goal.objects.filter(user=self.user)).count())
        daily_task_count = 0
        for p in Plan.objects.filter(
            goal__in=Goal.objects.filter(user=self.user)
        ).filter(continuous=True):
            daily_task_count += (p.add_count / p.add_period)
        report["daily_task_count"] = str(round(daily_task_count, 3))
        report["task_count"] = str(
            Task.objects.filter(
                plan__in=Plan.objects.filter(
                    goal__in=Goal.objects.filter(
                        user=self.user
                    )
                )
            ).count()
        )
        report["points_count"] = self.points
        return report


class Goal(models.Model):
    class PriorityLevels(models.TextChoices):
        BACKLOG = "0 BK", _("Backlog")
        LOW = "1 LW", _("Low")
        MEDIUM = "2 MD", _("Medium")
        HIGH = "3 HI", _("High")
        UG = "4 UG", _("Urgent")

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    priority = models.CharField(
        max_length=4, choices=PriorityLevels.choices, default=PriorityLevels.LOW
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def pull_report(self, *args, **kwargs):
        total = 0
        for p in Plan.objects.filter(goal=self):
            for t in Task.objects.filter(plan=p):
                total += 1
        return total


class TodoList(models.Model):
    class PriorityLevels(models.TextChoices):
        BACKLOG = "0 BK", _("Backlog")
        LOW = "1 LW", _("Low")
        MEDIUM = "2 MD", _("Medium")
        HIGH = "3 HI", _("High")
        UG = "4 UG", _("Urgent")

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.CharField(
        max_length=4, choices=PriorityLevels.choices, default=PriorityLevels.LOW
    )

    def __str__(self):
        return self.title


class Plan(models.Model):
    class PriorityLevels(models.TextChoices):
        BACKLOG = "0 BK", _("Backlog")
        LOW = "1 LW", _("Low")
        MEDIUM = "2 MD", _("Medium")
        HIGH = "3 HI", _("High")
        UG = "4 UG", _("Urgent")

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=20000)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    continuous = models.BooleanField(default=True)
    limit = models.IntegerField(default=10)
    add_count = models.IntegerField(default=1)
    default_priority = models.CharField(
        max_length=4, choices=PriorityLevels.choices, default=PriorityLevels.LOW
    )
    last_updated = models.DateField(
        "last_updated", default=datetime.date.today() - datetime.timedelta(days=366)
    )
    default_todolist = models.ForeignKey(
        TodoList, models.SET_NULL, blank=True, null=True
    )
    add_period = models.IntegerField(default=1)
    recurring_task_title = models.CharField(max_length=200, default="?")
    recurring_task_description = models.CharField(max_length=2000, default="?")
    default_points = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def task_count(self):
        return Task.objects.filter(plan=self).count()

    def user(self):
        return self.goal.user


class Task(models.Model):
    class PriorityLevels(models.TextChoices):
        BACKLOG = "0 BK", _("Backlog")
        LOW = "1 LW", _("Low")
        MEDIUM = "2 MD", _("Medium")
        HIGH = "3 HI", _("High")
        UG = "4 UG", _("Urgent")

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000, default="?")
    priority = models.CharField(
        max_length=4, choices=PriorityLevels.choices, default=PriorityLevels.LOW
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    todolist = models.ForeignKey(TodoList, models.SET_NULL, blank=True, null=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def is_due_soon(self):
        return self.due < timezone.now() + datetime.timedelta(days=2)

    def __str__(self):
        return self.title

    def user(self):
        return self.plan.goal.user

class Prize(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000, default="?")
    points = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def is_due_soon(self):
        return self.due < timezone.now() + datetime.timedelta(days=2)

    def __str__(self):
        return self.title
