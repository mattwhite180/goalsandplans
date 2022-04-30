import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    points_enabled = models.BooleanField(default=False)
    dark = models.BooleanField(default=False)

    def pull_report(self, *args, **kwargs):
        report = dict()
        report["goal_count"] = str(Goal.objects.filter(user=self.user).count())
        report["plan_count"] = str(
            Plan.objects.filter(goal__in=Goal.objects.filter(user=self.user)).count()
        )
        daily_task_count = 0
        for p in Plan.objects.filter(
            goal__in=Goal.objects.filter(user=self.user)
        ).filter(continuous=True):
            if not p.keep_at_limit:
                days_of_week = 0
                if p.monday:
                    days_of_week += 1
                if p.tuesday:
                    days_of_week += 1
                if p.wednesday:
                    days_of_week += 1
                if p.thursday:
                    days_of_week += 1
                if p.friday:
                    days_of_week += 1
                if p.saturday:
                    days_of_week += 1
                if p.sunday:
                    days_of_week += 1
                daily_task_count += days_of_week / 7
        report["daily_task_count"] = str(round(daily_task_count, 3))
        report["task_count"] = str(
            Task.objects.filter(
                plan__in=Plan.objects.filter(
                    goal__in=Goal.objects.filter(user=self.user)
                )
            ).count()
        )
        if self.points_enabled:
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
    hide_from_homepage = models.BooleanField(default=False)

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
    tasks_expire = models.BooleanField(default=False)
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
    hide_from_homepage = models.BooleanField(default=False)
    keep_at_limit = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    recurring_task_title = models.CharField(max_length=200, default="?")
    recurring_task_description = models.CharField(max_length=2000, default="?")
    default_points = models.IntegerField(default=1, blank=True, null=True)

    def __str__(self):
        return self.title

    def task_count(self):
        return Task.objects.filter(plan=self).count()

    def user(self):
        return self.goal.user

    def today(self):
        today_number = datetime.date.today().weekday()
        if (today_number == 0) and self.monday:
            return True
        if (today_number == 1) and self.tuesday:
            return True
        if (today_number == 2) and self.wednesday:
            return True
        if (today_number == 3) and self.thursday:
            return True
        if (today_number == 4) and self.friday:
            return True
        if (today_number == 5) and self.saturday:
            return True
        if (today_number == 6) and self.sunday:
            return True
        return False


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
    points = models.IntegerField(default=1)

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
    points = models.IntegerField(default=1, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def is_due_soon(self):
        return self.due < timezone.now() + datetime.timedelta(days=2)


class Issue(models.Model):
    obj_info = models.CharField(max_length=2000, default="?")
    where = models.CharField(max_length=2000, default="?")
    when = models.DateTimeField("when", default=datetime.datetime.now())
    exception_string = models.CharField(max_length=2000, default="?")
    ticket = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.exception_string[:10] + " (" + self.get_datetime() + ")"

    def get_datetime(self):
        return str(self.when.date())


class QuickNote(models.Model):
    class PriorityLevels(models.TextChoices):
        BACKLOG = "0 BK", _("Backlog")
        LOW = "1 LW", _("Low")
        MEDIUM = "2 MD", _("Medium")
        HIGH = "3 HI", _("High")
        UG = "4 UG", _("Urgent")

    title = models.CharField(max_length=200, default="QuickNote: ")
    description = models.CharField(max_length=2000, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.CharField(
        max_length=4, choices=PriorityLevels.choices, default=PriorityLevels.LOW
    )

    def __str__(self):
        return self.title + ":: " + self.description[:10]


class Archive(models.Model):
    created = models.DateTimeField("created", default=datetime.datetime.now())
    title = models.CharField(max_length=201, default="?")
    description = models.CharField(max_length=2001, default="?")

    def consume_task(self, task):
        self.title = task.title[:200]
        self.description = task.description[:2000]

    def get_datetime(self):
        return str(self.created.date())


class Pic(models.Model):
    title = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    description = models.CharField(max_length=2000, default="?")
    attribute = models.CharField(max_length=300)

    def __str__(self):
        return self.title