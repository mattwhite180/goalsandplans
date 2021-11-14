from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse

from .models import Goal, Plan, Task
from .forms import GoalForm, PlanForm, TaskForm

def loginPage(request):
    pass

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
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)

    form = PlanForm(request.POST, use_required_attribute=False)

    if form.is_valid():
        p = form.save(commit=False)
        p.goal = g
        p.save()

    r = g.pull_report()
    plan_list = Plan.objects.filter(goal=g)
    context = {
        'goal': g,
        'plan_list' : plan_list,
        'percentage': r['t'] / r['d'] if r['d'] != 0 else 0,
        'done': r['d'],
        'total': r['t'],
        'todo': r['t'] - r['d'],
        'form': form
    }
    return render(request, "planapp/goals.html", context)

def plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)

    form = TaskForm(request.POST, use_required_attribute=False)

    if form.is_valid():
        t = form.save(commit=False)
        t.plan = p
        t.save()

    task_list = Task.objects.filter(plan=p)
    context = {
        'plan': p,
        'task_list' : task_list,
        'form': form
    }
    return render(request, "planapp/plan.html", context)

def task(request, task_id):
    context = {}

    # t = get_object_or_404(Task, pk=task_id)

    # task_list = Task.objects.filter(plan=p)
    # context = {
    #     'plan': p,
    #     'task_list' : task_list,
    #     'form': form
    # }
    return render(request, "planapp/task.html", context)
