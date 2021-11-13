from django import forms
from django.forms import ModelForm#, Textarea, DateTimeField, MultipleChoiceField

from .models import Goal, Plan, Task

class GoalForm(forms.ModelForm):

    class Meta:
        model = Goal
        # fields = "__all__"
        fields = ('title', 'description', 'due', 'priority', 'cost')
        widgets = {
            'description': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
            'due' : forms.SelectDateWidget(),
            'priority' : forms.RadioSelect(choices=Goal.PriorityLevels)
        }
        # exclude = ['Cost']