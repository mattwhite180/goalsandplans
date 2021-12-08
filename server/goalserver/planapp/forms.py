from django import forms
from django.forms import ModelForm  # , Textarea, DateTimeField, MultipleChoiceField
from .models import Goal, Plan, Task, MiniTodo


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ("title", "description", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.RadioSelect(choices=Goal.PriorityLevels),
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
            "default_priority": forms.RadioSelect(choices=Plan.PriorityLevels),
        }


class QuickTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "priority", "minitodo", "plan")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.RadioSelect(choices=Task.PriorityLevels),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "priority", "minitodo")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.RadioSelect(choices=Task.PriorityLevels),
        }


class MiniTodoForm(forms.ModelForm):
    class Meta:
        model = MiniTodo
        fields = ("title", "description", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"cols": 20, "rows": 10}),
            "priority": forms.RadioSelect(choices=Goal.PriorityLevels),
        }
