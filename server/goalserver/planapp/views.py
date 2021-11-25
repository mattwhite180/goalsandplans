from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Goal, Plan, Task
from django.contrib.auth import authenticate, login
from .forms import GoalForm, PlanForm, TaskForm
from django.core.management import call_command
import json


def userOwnsGoal(u, g):
    return g.user.id == u.id

def userOwnsPlan(u, p):
    g = p.goal
    return userOwnsGoal(u, g)

def userOwnsTask(u, t):
    p = t.plan
    return userOwnsPlan(u, p)

def get_errors(f):
    errorList = list()
    myDict = json.loads(f.errors.as_json())
    for i in myDict:
        errors = myDict[i]
        for error in errors:
            errorList.append(error['message'])
    errorList.sort()
    return errorList


def create_account(request):
    context = dict()

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():
            u = form.save()
            u.save()
            login(request, u)
            return redirect("home")

        else:
            context['error_list'] = get_errors(form)

    else:
        form = UserCreationForm()

    context['form'] = form
    return render(request, 'planapp/createaccount.html', context)

def run_jobs(request):
    call_command('crontask')
    return redirect("home")

def handler404(request, exception=None):
    return HttpResponseRedirect(reverse('home'))

def index(request):
    context = {}

    return render(request, 'planapp/index.html', context)

def home(request):
    context = {}

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        #form = GoalForm(request.POST or None, request.FILES or None)
        form = GoalForm(request.POST)

        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
        else:
            context['error_list'] = get_errors(form)

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

    if not userOwnsGoal(request.user, g):
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':

        form = PlanForm(request.POST)

        if form.is_valid():
            p = form.save(commit=False)
            p.goal = g
            p.save()
        else:
            context['error_list'] = get_errors(form)

    else:
        form = PlanForm()

    plan_list = Plan.objects.filter(goal=g)
    context = {
        'goal': g,
        'plan_list' : plan_list,
        'todo': g.pull_report(),
        'form': form
    }
    return render(request, "planapp/goals.html", context)

@login_required
def edit_goal(request, goal_id):
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)

    if not userOwnsGoal(request.user, g):
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        #form = GoalForm(request.POST or None, request.FILES or None)
        form = GoalForm(request.POST, instance=g)

        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
            return HttpResponseRedirect(reverse('goal', args=(goal_id,)))
        else:
            context['error_list'] = get_errors(form)

    else:
        form = GoalForm(instance=g)
    
    context['form'] = form
    return render(request, "planapp/formedit.html", context)
    # return HttpResponseRedirect(reverse(home))


@login_required
def edit_plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)

    if not userOwnsPlan(request.user, p):
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        #form = GoalForm(request.POST or None, request.FILES or None)
        form = PlanForm(request.POST, instance=p)

        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            return HttpResponseRedirect(reverse('plan', args=(plan_id,)))
        else:
            context['error_list'] = get_errors(form)

    else:
        form = PlanForm(instance=p)
    
    context['form'] = form
    return render(request, "planapp/formedit.html", context)


@login_required
def edit_task(request, task_id):
    context = {}

    t = get_object_or_404(Task, pk=task_id)

    if not userOwnsTask(request.user, t):
        return HttpResponseRedirect(reverse('home'))

    if request.method == 'POST':
        #form = GoalForm(request.POST or None, request.FILES or None)
        form = TaskForm(request.POST, instance=t)

        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            return HttpResponseRedirect(reverse('task', args=(task_id,)))
        else:
            context['error_list'] = get_errors(form)

    else:
        form = TaskForm(instance=t)
    
    context['form'] = form
    return render(request, "planapp/formedit.html", context)

@login_required
def delete_task(request, task_id):

    context = {}

    t = get_object_or_404(Task, pk=task_id)
    plan_id = t.plan.id
    
    if not userOwnsTask(request.user, t):
        return HttpResponseRedirect(reverse('home'))

    t.delete()

    return HttpResponseRedirect(reverse('plan', args=(plan_id,)))


@login_required
def delete_plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)
    goal_id = p.goal
    
    if not userOwnsPlan(request.user, p):
        return HttpResponseRedirect(reverse('home'))


    p.delete()

    return HttpResponseRedirect(reverse('goal', args=(goal_id,)))


@login_required
def delete_goal(request, goal_id):
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)
    
    if not userOwnsGoal(request.user, g):
        return HttpResponseRedirect(reverse('home'))


    g.delete()

    return HttpResponseRedirect(reverse('home'))


@login_required
def plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)

    if not userOwnsPlan(request.user, p):
        return HttpResponseRedirect(reverse('home'))

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

    t = get_object_or_404(Task, pk=task_id)

    if not userOwnsTask(request.user, t):
        return HttpResponseRedirect(reverse('home'))



    context = {'task': t}

    return render(request, "planapp/task.html", context)


@login_required
def task_todo(request):
    context = {}

    goal_list = Goal.objects.filter(user=request.user)
    plan_list = Plan.objects.filter(goal__in=goal_list)
    task_list = Task.objects.filter(plan__in=plan_list).order_by('-priority')

    context = {'task_list': task_list}

    return render(request, "planapp/todo.html", context)
