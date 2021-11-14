from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Goal, Plan, Task
from django.contrib.auth import authenticate, login
from .forms import GoalForm, PlanForm, TaskForm


def create_account(request):
    context = dict()

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():
            u = form.save()
            u.save()
            if u is not None:
                login(request, u)
                return redirect("home")
            else:
                return render(request, 'planapp/index.html', {})

    else:
        form = UserCreationForm()

    context['form'] = form
    return render(request, 'planapp/createaccount.html', context)


def index(request):
    context = {}

    return render(request, 'planapp/index.html', context)

@login_required
def home(request):
    context = {}

    if not request.user.is_authenticated:
        return render(request, 'planapp/index.html', context)

    
    if request.method == 'POST':
        #form = GoalForm(request.POST or None, request.FILES or None)
        form = GoalForm(request.POST)

        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
    
    else:
        form = GoalForm()

    context['form'] = form
    goals_list = Goal.objects.filter(user=request.user)
    context['goals_list'] = goals_list

    return render(request, 'planapp/home.html', context)

@login_required
def goal(request, goal_id):
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)

    if request.method == 'POST':

        form = PlanForm(request.POST)

        if form.is_valid():
            p = form.save(commit=False)
            p.goal = g
            p.save()

    else:
        form = PlanForm()

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

@login_required
def plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)

    if request.method == 'POST':

        form = TaskForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            t = form.save(commit=False)
            t.plan = p
            t.save()

    else:
        form = TaskForm()

    task_list = Task.objects.filter(plan=p)
    context = {
        'plan': p,
        'task_list' : task_list,
        'form': form
    }
    return render(request, "planapp/plan.html", context)

@login_required
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
