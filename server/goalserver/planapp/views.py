import json
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AnonymousUser, User
from django.core import serializers
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (BackupCreateForm, GoalForm, PlanForm, QuickTaskForm,
                    TaskForm, TodoListForm)
from .models import Goal, Plan, Task, TodoList


"""
#####
Helpful functions used by views
"""


def debug():
    return settings.DEBUG


def data_to_json(user_id=-1):
    dataList = list()
    if user_id == -1:
        return dataToJsonAll()

    u = User.objects.get(id=user_id)
    dataList.insert(len(dataList), {"user": {"username": u.username}})
    goal_list = Goal.objects.filter(user=u).order_by("title")
    plan_list = Plan.objects.filter(goal__in=goal_list).order_by("title")
    plan_noncontinuous_list = plan_list.filter(continuous=False)
    task_list = Task.objects.filter(plan__in=plan_noncontinuous_list)
    dataList.insert(len(dataList), json.loads(serializers.serialize("json", goal_list)))
    dataList.insert(len(dataList), json.loads(serializers.serialize("json", plan_list)))
    dataList.insert(len(dataList), json.loads(serializers.serialize("json", task_list)))
    return json.dumps(dataList)


def mobile(request):
    # Return True if the request comes from a mobile device.
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META["HTTP_USER_AGENT"]):
        return True
    else:
        return False


def get_context(request):
    call_command("crontask")
    context = {}
    context["is_mobile"] = mobile(request)
    context["debug"] = debug()
    return context


def create_backup(request):
    context = get_context(request)
    if request.user.is_superuser or request.user.is_staff:
        if request.method == "POST":
            form = BackupCreateForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user_id = cd.get("user").id
                context["data"] = dataToJson(user_id)
        else:
            form = BackupCreateForm()
            context["form"] = form

        return render(request, "planapp/backup.html", context)
    else:
        return HttpResponseRedirect(reverse("home"))


def message_generator(verb, obj):
    if hasattr(obj, "title"):
        name = obj.title
    elif hasattr(obj, "username"):
        name = obj.username
    else:
        name = "(instance name)"

    try:
        model_name = obj._meta.model_name
    except:
        model_name = "User"
    return (
        str(verb)
        + " a "
        + str(model_name)
        + ": "
        + str(name)
        + " (id="
        + str(obj.id)
        + ")"
    )


def unauthorized_message(request, obj):
    val = "object"
    try:
        val = str(obj._meta.model_name)
    except:
        pass
    messages.warning(request, "you are not the owner of this " + val)


def get_errors(f):
    errorList = list()
    myDict = json.loads(f.errors.as_json())
    for i in myDict:
        errors = myDict[i]
        for error in errors:
            errorList.append(error["message"])
    errorList.sort()
    return errorList


"""
#####
Non-model views
"""


def create_account(request):
    context = get_context(request)

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            u = form.save()
            u.save()
            login(request, u)
            messages.success(request, message_generator("created", u))
            return redirect("home")

        else:
            context["error_list"] = get_errors(form)

    else:
        form = UserCreationForm()

    context["form"] = form
    return render(request, "planapp/createaccount.html", context)


def run_jobs(request):
    call_command("crontask")
    messages.success(request, "ran cron task")
    return redirect("home")


def handler404(request, exception=None):
    messages.error(request, "404: Page not found. Redirecting to home")
    return HttpResponseRedirect(reverse("home"))


def index(request):
    context = get_context(request)

    return render(request, "planapp/index.html", context)


def about(request):
    context = get_context(request)

    return render(request, "planapp/about.html", context)


def home(request):
    context = get_context(request)

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = GoalForm(request.POST)

        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
            messages.success(request, message_generator("created", g))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = GoalForm()

    context["form"] = form
    goals_list = Goal.objects.filter(user=request.user).order_by("-priority", "title")
    context["goals_list"] = goals_list

    return render(request, "planapp/home.html", context)


def search_list(request):
    context = get_context(request)

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    goal_list = Goal.objects.filter(user=request.user.id).order_by("-priority", "title")
    plan_list = Plan.objects.filter(goal__in=goal_list).order_by(
        "-default_priority", "title"
    )
    plan_noncontinuous_list = plan_list.filter(continuous=False)
    task_list = Task.objects.filter(plan__in=plan_noncontinuous_list).order_by(
        "-priority", "title"
    )
    todo_list = TodoList.objects.filter(user=request.user.id).order_by(
        "-priority", "title"
    )

    context["goal_list"] = goal_list
    context["plan_list"] = plan_list
    context["task_list"] = task_list
    context["todo_list"] = todo_list

    return render(request, "planapp/search-list.html", context)


"""
#####
Goal Views
"""


@login_required
def goal(request, goal_id):
    context = get_context(request)

    g = get_object_or_404(Goal, pk=goal_id)

    if request.user.id is not g.user.id:
        unauthorized_message(request, g)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":

        form = PlanForm(request.POST)

        if form.is_valid():
            p = form.save(commit=False)
            p.goal = g
            p.save()
            messages.success(request, message_generator("created", p))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = PlanForm()
        form.fields["default_todolist"].queryset = TodoList.objects.filter(
            user=request.user
        ).order_by("title")

    plan_list = Plan.objects.filter(goal=g).order_by("-default_priority", "title")
    context["goal"] = g
    context["plan_list"] = plan_list
    context["todo"] = g.pull_report()
    context["form"] = form
    return render(request, "planapp/goal.html", context)


@login_required
def edit_goal(request, goal_id):
    context = get_context(request)

    g = get_object_or_404(Goal, pk=goal_id)

    if request.user.id is not g.user.id:
        unauthorized_message(request, g)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = GoalForm(request.POST, instance=g)

        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
            messages.info(request, message_generator("edited", g))
            return HttpResponseRedirect(reverse("goal", args=(goal_id,)))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = GoalForm(instance=g)

    context["form"] = form
    context["form_title"] = "edit goal (" + str(g.title) + ")"
    return render(request, "planapp/formedit.html", context)
    # return HttpResponseRedirect(reverse(home))


@login_required
def delete_goal(request, goal_id):
    context = get_context(request)

    g = get_object_or_404(Goal, pk=goal_id)

    if request.user.id is g.user.id:
        for p in Plan.objects.filter(goal=g):
            messages.warning(request, message_generator("deleted", p))
            for t in Task.objects.filter(plan=p):
                messages.warning(request, message_generator("deleted", t))
        messages.warning(request, message_generator("deleted", g))
        g.delete()
    else:
        unauthorized_message(request, g)

    return HttpResponseRedirect(reverse("home"))


"""
#####
Plan Views
"""


@login_required
def plan(request, plan_id):
    context = get_context(request)

    p = get_object_or_404(Plan, pk=plan_id)

    if request.user.id is not p.user().id:
        unauthorized_message(request, p)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":

        form = TaskForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            t = form.save(commit=False)
            t.plan = p
            t.save()
            messages.success(request, message_generator("created", t))

    else:
        form = TaskForm()
        form.fields["todolist"].queryset = TodoList.objects.filter(
            user=request.user
        ).order_by("title")

    task_list = Task.objects.filter(plan=p).order_by("-priority", "title")
    context["plan"] = p
    context["task_list"] = task_list
    context["form"] = form
    return render(request, "planapp/plan.html", context)


@login_required
def edit_plan(request, plan_id):
    context = get_context(request)

    p = get_object_or_404(Plan, pk=plan_id)

    if request.user.id is not p.user().id:
        unauthorized_message(request, p)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = PlanForm(request.POST, instance=p)

        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            messages.info(request, message_generator("edited", p))
            return HttpResponseRedirect(reverse("plan", args=(plan_id,)))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = PlanForm(instance=p)

    context["form"] = form
    context["form_title"] = "edit plan (" + str(p.title) + ")"
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_plan(request, plan_id):
    context = get_context(request)

    p = get_object_or_404(Plan, pk=plan_id)
    goal_id = p.goal.id

    if request.user.id is p.user().id:
        for t in Task.objects.filter(plan=p):
            messages.warning(request, message_generator("deleted", t))
        messages.warning(request, message_generator("deleted", p))
        p.delete()
    else:
        unauthorized_message(request, p)

    return HttpResponseRedirect(reverse("goal", args=(goal_id,)))


"""
#####
Task Views
"""


@login_required
def task(request, task_id):
    context = get_context(request)

    t = get_object_or_404(Task, pk=task_id)

    if request.user.id is not t.user().id:
        unauthorized_message(request, t)
        return HttpResponseRedirect(reverse("home"))

    context["task"] = t
    return render(request, "planapp/task.html", context)


@login_required
def edit_task(request, task_id):
    context = get_context(request)

    t = get_object_or_404(Task, pk=task_id)

    if request.user.id is not t.user().id:
        unauthorized_message(request, t)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = TaskForm(request.POST, instance=t)

        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.info(request, message_generator("edited", t))
            return HttpResponseRedirect(reverse("task", args=(task_id,)))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = TaskForm(instance=t)
        form.fields["todolist"].queryset = TodoList.objects.filter(
            user=request.user
        ).order_by("title")

    context["form"] = form
    context["form_title"] = "edit task (" + str(t.title) + ")"
    return render(request, "planapp/formedit.html", context)


@login_required
def task_remove_todo(request, task_id):
    context = get_context(request)

    t = get_object_or_404(Task, pk=task_id)

    if request.user.id is t.user().id:
        unauthorized_message(request, t)
        return HttpResponseRedirect(reverse("home"))

    t.todolist = None
    t.save()

    context["task"] = t
    return render(request, "planapp/task.html", context)


@login_required
def delete_task(request, task_id):

    context = get_context(request)

    t = get_object_or_404(Task, pk=task_id)
    plan_id = t.plan.id

    if request.user.id is t.user().id:
        messages.warning(request, message_generator("deleted", t))
        t.delete()
    else:
        unauthorized_message(request, t)

    return HttpResponseRedirect(reverse("plan", args=(plan_id,)))


@login_required
def quick_task(request):
    context = get_context(request)

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = QuickTaskForm(request.POST)

        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.info(request, message_generator("created", t))
            return HttpResponseRedirect(reverse("home"))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = QuickTaskForm()
        goal_list = Goal.objects.filter(user=request.user)
        form.fields["plan"].queryset = Plan.objects.filter(goal__in=goal_list).order_by(
            "title"
        )
        form.fields["todolist"].queryset = TodoList.objects.filter(
            user=request.user
        ).order_by("title")

    context["form"] = form
    context["form_title"] = "create a task"
    return render(request, "planapp/formedit.html", context)


"""
#####
TodoList Views
"""


@login_required
def task_todo(request):
    context = get_context(request)

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":

        form = TodoListForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.success(request, message_generator("created", m))

    else:
        form = TodoListForm()

    goal_list = Goal.objects.filter(user=request.user)
    plan_list = Plan.objects.filter(goal__in=goal_list)
    task_list = Task.objects.filter(plan__in=plan_list).order_by("-priority", "title")

    context["task_list"] = task_list
    context["form"] = form
    context["todolist_list"] = TodoList.objects.filter(user=request.user).order_by(
        "-priority", "title"
    )

    return render(request, "planapp/todo.html", context)


@login_required
def todolist(request, todo_id):
    context = get_context(request)

    m = get_object_or_404(TodoList, pk=todo_id)

    if m.user.id != request.user.id:
        unauthorized_message(request, m)
        return HttpResponseRedirect(reverse("home"))

    task_list = Task.objects.filter(todolist=m).order_by("-priority", "title")
    context["todolist"] = m
    context["task_list"] = task_list
    return render(request, "planapp/todolist.html", context)


@login_required
def edit_todolist(request, todo_id):
    context = get_context(request)

    m = get_object_or_404(TodoList, pk=todo_id)

    if request.user.id != m.user.id:
        unauthorized_message(request, m)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = TodoListForm(request.POST, instance=m)

        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.info(request, message_generator("edited", m))
            return HttpResponseRedirect(reverse("todolist", args=(todo_id,)))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = TaskForm(instance=m)

    context["form"] = form
    context["form_title"] = "edit todolist (" + str(m.title) + ")"
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_todolist(request, todo_id):

    context = get_context(request)

    m = get_object_or_404(TodoList, pk=todo_id)

    if request.user.id == m.user.id:
        messages.warning(request, message_generator("deleted", m))
        m.delete()
    else:
        unauthorized_message(request, m)

    return HttpResponseRedirect(reverse("task_todo"))
