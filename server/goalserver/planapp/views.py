from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse

from .models import Goal, Plan, Task
from .forms import GoalForm

def index(request):
    context = {}

    #form = GoalForm(request.POST or None, request.FILES or None)
    form = GoalForm(request.POST, use_required_attribute=False)

    if form.is_valid():
        g = form.save()
        g.save()

    context['form'] = form

    goals_list = Goal.objects.all()
    context['goals_list'] = goals_list

    return render(request, 'planapp/index.html', context)

def goal(request, goal_id):
    g = get_object_or_404(Goal, pk=goal_id)
    r = g.pull_report()
    plan_list = Plan.objects.filter(goal=g)
    context = {
        'goal': g,
        'percentage': r['t'] / r['d'],
        'done': r['d'],
        'total': r['t'],
        'todo': r['t'] - r['d']
    }

def plan(request):
    pass

def task(request):
    pass