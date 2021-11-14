from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Goal, Plan, Task
from .forms import GoalForm, PlanForm, TaskForm

# def logout_view(request):
#     logout(request)
#     return HttpResponseRedirect(reverse("index"))

# def login_view(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return HttpResponseRedirect(reverse("home"))
#     else:
#         return render(request, 'planapp/index.html', {})

def index(request):
    context = {}

    # #form = GoalForm(request.POST or None, request.FILES or None)
    # form = GoalForm(request.POST, use_required_attribute=False)
    # login_form = AuthenticationForm(request.POST)
    # create_form = UserCreationForm(request.POST)

    # if login_form.is_valid():
        
    
    # if create_form.is_valid():
    #     u = create_form.save()
    #     u.save()

    # context['login_form'] = login_form
    # context['create_form'] = create_form
    # context['loggedin'] = request.user.is_authenticated

    # goals_list = Goal.objects.all()
    # context['goals_list'] = goals_list

    return render(request, 'planapp/index.html', context)

@login_required
def home(request):
    context = {}

    #form = GoalForm(request.POST or None, request.FILES or None)
    form = GoalForm(request.POST, use_required_attribute=False)

    if form.is_valid():
        g = form.save()
        g.save()

    context['form'] = form
    context['loggedin'] = request.user.is_authenticated

    goals_list = Goal.objects.all()
    context['goals_list'] = goals_list

    return render(request, 'planapp/home.html', context)

@login_required
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

@login_required
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
