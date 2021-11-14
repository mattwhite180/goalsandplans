from django import forms
from django.forms import ModelForm#, Textarea, DateTimeField, MultipleChoiceField
from django.contrib.auth.models import User
from .models import Goal, Plan, Task

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class GoalForm(forms.ModelForm):

    class Meta:
        model = Goal
        fields = ('title', 'description', 'due', 'priority', 'cost')
        widgets = {
            'description': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
            'due' : forms.SelectDateWidget(),
            'priority' : forms.RadioSelect(choices=Goal.PriorityLevels)
        }

class PlanForm(forms.ModelForm):

    class Meta:
        model = Plan
        fields = (
            'title',
            'description',
            'continuous',
            'limit',
            'add_count',
            'add_per_day',
            'recurring_task_title',
            'recurring_task_description',
            'default_priority'
        )
        widgets = {
            'description': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
            'recurring_task_description': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
            'default_priority' : forms.RadioSelect(choices=Goal.PriorityLevels)
        }

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = (
            'title',
            'description',
            'due',
            'finished',
            'priority',
            'active',
            'cost'
        )
        widgets = {
            'description': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
            'priority' : forms.RadioSelect(choices=Goal.PriorityLevels),
            'due' : forms.SelectDateWidget(),
        }