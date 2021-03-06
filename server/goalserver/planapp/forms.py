from django import forms
from django.contrib.auth.models import User

from .models import Goal, Plan, Prize, QuickNote, Task, TodoList, UserData


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ("title", "description", "priority", "default_pic")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Goal.PriorityLevels),
        }


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = (
            "title",
            "description",
            "goal",
            "continuous",
            "limit",
            "add_count",
            "tasks_expire",
            "keep_at_limit",
            "hide_from_homepage",
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "recurring_task_title",
            "recurring_task_description",
            "default_points",
            "default_priority",
            "default_todolist",
            "default_pic",
        )
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "recurring_task_description": forms.Textarea(
                attrs={"cols": 20, "rows": 10}
            ),
            "default_priority": forms.Select(choices=Plan.PriorityLevels),
        }


class QuickTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "points",
            "priority",
            "todolist",
            "plan"
        )
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Task.PriorityLevels),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "title",
            "plan",
            "description",
            "points",
            "priority",
            "todolist",
            "pic"
        )
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Task.PriorityLevels),
        }


class TodoListForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = ("title", "description", "priority", "hide_from_homepage")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Goal.PriorityLevels),
        }


class PrizeForm(forms.ModelForm):
    class Meta:
        model = Prize
        fields = ("title", "description", "points")
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "cols": 20,
                    "rows": 10
                }
            )
        }


class QuickNoteForm(forms.ModelForm):
    class Meta:
        model = QuickNote
        fields = ("title", "description", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=QuickNote.PriorityLevels),
        }


class UserDataForm(forms.ModelForm):
    class Meta:
        model = UserData
        fields = ("dark", "points_enabled", "points", "default_pic")


class ChangePointsForm(forms.Form):
    amount = forms.IntegerField(initial=1)


class RedeemPrizeForm(forms.Form):
    count = forms.IntegerField(initial=1)


class BackupCreateForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class EnablePrizeForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    choice = forms.BooleanField()
