from django import forms
from django.forms import ModelForm  # , Textarea, DateTimeField, MultipleChoiceField
from .models import Goal, Plan, Task, TodoList
from django.contrib.auth.models import AnonymousUser, User


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ("title", "description", "priority")
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
            "continuous",
            "limit",
            "add_count",
            "add_period",
            "recurring_task_title",
            "recurring_task_description",
            "default_priority",
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
        fields = ("title", "description", "priority", "todolist", "plan")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Task.PriorityLevels),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "priority", "todolist")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Task.PriorityLevels),
        }


class TodoListForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = ("title", "description", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.Select(choices=Goal.PriorityLevels),
        }


class BackupCreateForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
