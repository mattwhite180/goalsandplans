import datetime
import json
import re

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core import serializers
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (BackupCreateForm, ChangePointsForm, EnablePrizeForm,
                    GoalForm, PlanForm, PrizeForm, QuickNoteForm,
                    QuickTaskForm, RedeemPrizeForm, TaskForm, TodoListForm,
                    UserDataForm)
from .models import (Archive, Goal, Issue, Plan, Prize, QuickNote, Task, TodoList,
                     UserData)


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
    context = {}
    context["is_mobile"] = mobile(request)
    context["debug"] = debug()
    if request.user.is_authenticated:
        if UserData.objects.filter(user=request.user).count() > 0:
            ud = UserData.objects.get(user=request.user)
        else:
            ud = UserData.objects.create(user=request.user)
        context["user_data"] = ud.pull_report()
        context["points_enabled"] = ud.points_enabled
        context["dark"] = ud.dark
    return context


def issues(request):
    context = get_context(request)
    context["issue_list"] = Issue.objects.all().order_by("-when")
    return render(request, "planapp/issues.html", context)


def delete_issue(request, issue_id):
    context = get_context(request)
    i = get_object_or_404(Issue, pk=issue_id)
    i_title = str(i)
    i.delete()
    messages.success(request, str("deleted issue '" + i_title + "': " + str(issue_id)))
    return render(request, "planapp/issues.html", context)


def planify(request):
    context = get_context(request)
    if request.user.is_superuser or request.user.is_staff:
        call_command("planify")
        messages.success(request, "planify command ran")
    return HttpResponseRedirect(reverse("home"))


def taskify(plan):
    count = 0
    if not plan.continuous:
        return 0
    deltaDate = datetime.date.today() - plan.last_updated
    if (deltaDate.days >= 1 and plan.today()) or plan.keep_at_limit:
        try:
            if plan.tasks_expire and not plan.today():
                for t in Tasks.objects.filter(plan=plan):
                    t.delete()
        except:
            i = Issue.objects.create(
                obj_info="Plan: " + str(plan.id),
                where="taskify (delete expired tasks)",
                exception_string=str(e),
            )
        try:
            for i in range(plan.add_count):
                currentCount = Task.objects.filter(plan=plan).count()
                if currentCount < plan.limit:
                    newT = Task.objects.create(
                        title=plan.recurring_task_title,
                        description=plan.recurring_task_description,
                        priority=plan.default_priority,
                        plan=plan,
                        points=plan.default_points,
                    )
                    if plan.default_todolist:
                        newT.todolist = plan.default_todolist
                    newT.save()
                    count += 1
            plan.last_updated = datetime.date.today()
            plan.save()
        except Exception as e:
            i = Issue.objects.create(
                obj_info="Plan: " + str(plan.id),
                where="taskify (create new tasks)",
                exception_string=str(e),
            )
            i.save()
    return count


def enable_prizes(request):
    context = get_context(request)
    if request.user.is_authenticated and (
        request.user.is_superuser or request.user.is_staff
    ):
        if request.method == "POST":
            form = EnablePrizeForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user_id = cd.get("user").id
                choice = cd.get("choice")
                if UserData.objects.filter(user=user_id).count() > 0:
                    ud = UserData.objects.get(user=user_id)
                else:
                    ud = UserData.objects.create(user=user_id)
                ud.points_enabled = choice
                ud.save()
                messages.success(
                    request,
                    "enabled/disabled the user " + str(ud.user.username) + "'s point",
                )
                return HttpResponseRedirect(reverse("home"))
        form = EnablePrizeForm()
        context["form"] = form
        return render(request, "planapp/formedit.html", context)
    return HttpResponseRedirect(reverse("home"))


def create_backup(request):
    context = get_context(request)
    if request.user.is_authenticated and (
        request.user.is_superuser or request.user.is_staff
    ):
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


def point_changer(request, points):
    if request.user.is_authenticated:
        ud = UserData.objects.get(user=request.user)
        ud.points += points
        ud.save()
        return True
    else:
        return False


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
            user_data = UserData.objects.create(user=u)
            user_data.save()
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
    count = 0
    for plan in Plan.objects.filter(continuous=True):
        count += taskify(plan)
    messages.success(request, "ran taskify. created " + str(count) + " tasks")
    return redirect("home")


def custom_error_handle(request, exception=None):
    s = str(request)
    i = Issue.objects.create(
        obj_info="n/a", where="custom error handling", exception_string=s,
    )
    i.save()
    messages.error(request, "An exception occurred at " + str(s))
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
    goal_list = Goal.objects.filter(user=request.user).order_by("-priority", "title")
    context["goal_list"] = goal_list

    return render(request, "planapp/home.html", context)


def userdata(request):
    context = get_context(request)

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    ud = UserData.objects.get(user=request.user)

    if request.method == "POST":

        form = UserDataForm(request.POST, instance=ud)

        if form.is_valid():
            ud = form.save(commit=False)
            ud.save()
            messages.info(request, "edited user data")
            return HttpResponseRedirect(reverse("home"))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = UserDataForm(instance=ud)

    context["form"] = form
    context["form_title"] = "Edit user data"
    return render(request, "planapp/formedit.html", context)


def change_points(request):
    context = get_context(request)

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = ChangePointsForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            amount = cd.get("amount")
            ud = UserData.objects.get(user=request.user)
            before = ud.points
            ud.points = amount
            ud.save()
            messages.success(
                request,
                str(
                    "user's points counts changed from "
                    + str(before)
                    + " to "
                    + str(amount)
                ),
            )
            return HttpResponseRedirect(reverse("home"))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = ChangePointsForm()

    context["form"] = form
    goals_list = Goal.objects.filter(user=request.user).order_by("-priority", "title")
    context["goals_list"] = goals_list

    return render(request, "planapp/changepoints.html", context)


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

    goal_list = Goal.objects.filter(id=goal_id)
    if len(goal_list) == 0:
        messages.error(request, f"could not find goal of id: { goal_id }")
        return HttpResponseRedirect(reverse("home"))

    g = goal_list[0]

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
        if context["points_enabled"] == False:
            form.fields["default_points"].widget = forms.HiddenInput()

    plan_list = Plan.objects.filter(goal=g).order_by("-default_priority", "title")
    for p in plan_list:
        taskify(p)
    context["goal_list"] = goal_list
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
            delete_plan(request, p.id)
        messages.warning(request, message_generator("deleted", g))
        a = Archive.objects.create()
        a.consume_task(g)
        a.save()
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

    plan_list = Plan.objects.filter(id=plan_id)
    for p in plan_list:
        taskify(p)
    if len(plan_list) == 0:
        messages.error(request, f"could not find plan of id: { plan_id }")
        return HttpResponseRedirect(reverse("home"))
    p = plan_list[0]

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
        if context["points_enabled"] == False:
            form.fields["points"].widget = forms.HiddenInput()

    task_list = Task.objects.filter(plan=p).order_by("-priority", "title")
    context["plan_list"] = plan_list
    context["task_list"] = task_list
    context["form"] = form
    return render(request, "planapp/plan.html", context)


@login_required
def plan_create_task(request, plan_id):
    context = get_context(request)

    p = get_object_or_404(Plan, pk=plan_id)

    if request.user.id is not p.user().id:
        unauthorized_message(request, p)
        return HttpResponseRedirect(reverse("home"))

    newT = Task.objects.create(
        title=p.recurring_task_title,
        description=p.recurring_task_description,
        priority=p.default_priority,
        plan=p,
        points=p.default_points,
    )
    newT.save()
    if context["points_enabled"]:
        point_changer(request, 1)
    return HttpResponseRedirect(reverse("plan", args=(plan_id,)))


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
        if context["points_enabled"] == False:
            form.fields["default_points"].widget = forms.HiddenInput()

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
            delete_task(request, t.id, True)
        messages.warning(request, message_generator("deleted", p))
        a = Archive.objects.create()
        a.consume_task(p)
        a.save()
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

    task_list = Task.objects.filter(id=task_id)
    if len(task_list) == 0:
        messages.error(request, f"could not find task of id: { task_id }")
        return HttpResponseRedirect(reverse("home"))
    t = task_list[0]

    if request.user.id is not t.user().id:
        unauthorized_message(request, t)
        return HttpResponseRedirect(reverse("home"))

    context["task_list"] = task_list
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
        if context["points_enabled"] == False:
            form.fields["points"].widget = forms.HiddenInput()

    context["form"] = form
    context["form_title"] = "edit task (" + str(t.title) + ")"
    return render(request, "planapp/formedit.html", context)


@login_required
def task_remove_todo(request, task_id):
    context = get_context(request)

    t = get_object_or_404(Task, pk=task_id)

    if request.user.id is not t.user().id:
        unauthorized_message(request, t)
        return HttpResponseRedirect(reverse("home"))

    t.todolist = None
    t.save()

    context["task"] = t
    return render(request, "planapp/task.html", context)


@login_required
def delete_task(request, task_id, redirect=None):

    context = get_context(request)

    t = get_object_or_404(Task, pk=task_id)
    plan_id = t.plan.id
    todolist_id = None
    if t.todolist:
        todolist_id = t.todolist.id

    if request.user.id is t.user().id:
        messages.warning(request, message_generator("deleted", t))
        point_changer(request, t.points)
        if not t.plan.continuous:
            a = Archive.objects.create()
            a.consume_task(t)
            a.save()
        t.delete()
    else:
        unauthorized_message(request, t)

    url = request.META.get("HTTP_REFERER")
    if url == None:
        return HttpResponseRedirect(reverse("plan", args=(plan_id,)))
    source = "https://goalsandplans101.com/"
    if debug():
        source = "http://localhost/"
    cut_url = url.replace(source, "")
    if cut_url[:9] == "task_todo":
        return HttpResponseRedirect(reverse("task_todo"))
    elif cut_url[:4] in ["plan", "task"]:
        return HttpResponseRedirect(reverse("plan", args=(plan_id,)))
    elif cut_url[:8] == "todolist" and todolist_id:
        return HttpResponseRedirect(reverse("todolist", args=(todolist_id,)))
    else:
        if not redirect:
            messages.warning(
                request, f"task redirect could not find a good match for the url: { url }"
            )
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
        if context["points_enabled"] == False:
            form.fields["points"].widget = forms.HiddenInput()

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
    for p in plan_list:
        taskify(p)
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

    todolist_list = TodoList.objects.filter(id=todo_id)
    if len(todolist_list) == 0:
        messages.error(request, f"could not find todolist of id: { todolist_list }")
        return HttpResponseRedirect(reverse("home"))
    m = todolist_list[0]

    if m.user.id != request.user.id:
        unauthorized_message(request, m)
        return HttpResponseRedirect(reverse("home"))

    task_list = Task.objects.filter(todolist=m).order_by("-priority", "title")
    context["todolist_list"] = todolist_list
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
        form = TodoListForm(instance=m)

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


"""
#####
Prize Views
"""


@login_required
def prize(request):
    context = get_context(request)

    if request.method == "POST":

        form = PrizeForm(request.POST)

        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            messages.success(request, message_generator("created", p))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = PrizeForm()

    prize_list = Prize.objects.filter(user=request.user).order_by("title")
    context["prize_list"] = prize_list
    context["form"] = form
    return render(request, "planapp/prize.html", context)


@login_required
def redeem_prize(request, prize_id):
    context = get_context(request)

    prize_list = Prize.objects.filter(id=prize_id)
    p = prize_list[0]

    if request.user.id != p.user.id:
        unauthorized_message(request, p)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":

        form = RedeemPrizeForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            count = cd.get("count")
            points_count = -1 * abs(count * p.points)
            point_changer(request, points_count)
            messages.success(request, "Redeemed " + str(abs(points_count)) + " points")
        else:
            context["error_list"] = get_errors(form)

    else:
        form = RedeemPrizeForm()

    context["form"] = form
    context["prize_list"] = prize_list
    return render(request, "planapp/redeem_prize.html", context)


@login_required
def edit_prize(request, prize_id):
    context = get_context(request)

    p = get_object_or_404(Prize, pk=prize_id)

    if request.user.id != p.user.id:
        unauthorized_message(request, p)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = PrizeForm(request.POST, instance=p)

        if form.is_valid():
            p = form.save(commit=False)
            p.save()
            messages.info(request, message_generator("edited", p))
            return HttpResponseRedirect(reverse("prize"))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = PrizeForm(instance=p)

    context["form"] = form
    context["form_title"] = "edit prize (" + str(p.title) + ")"
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_prize(request, prize_id):

    context = get_context(request)

    p = get_object_or_404(Prize, pk=prize_id)

    if request.user.id == p.user.id:
        messages.warning(request, message_generator("deleted", p))
        p.delete()
    else:
        unauthorized_message(request, p)

    return HttpResponseRedirect(reverse("prize"))


"""
#####
QuickNote Views
"""


@login_required
def quicknote(request):
    context = get_context(request)

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":

        form = QuickNoteForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.success(request, message_generator("created", m))

    else:
        form = QuickNoteForm()

    quicknote_list = QuickNote.objects.filter(user=request.user).order_by(
        "-priority", "title"
    )

    context["quicknote_list"] = quicknote_list
    context["form"] = form

    return render(request, "planapp/quicknote.html", context)


@login_required
def edit_quicknote(request, quicknote_id):
    context = get_context(request)

    m = get_object_or_404(QuickNote, pk=quicknote_id)

    if request.user.id != m.user.id:
        unauthorized_message(request, m)
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = QuickNoteForm(request.POST, instance=m)

        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.info(request, message_generator("edited", m))
            return HttpResponseRedirect(reverse("quicknote"))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = QuickNoteForm(instance=m)

    context["form"] = form
    context["form_title"] = "edit todolist (" + str(m.title) + ")"
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_quicknote(request, quicknote_id):

    context = get_context(request)

    m = get_object_or_404(QuickNote, pk=quicknote_id)

    if request.user.id == m.user.id:
        messages.warning(request, message_generator("deleted", m))
        a = Archive.objects.create()
        a.consume_task(m)
        a.save()
        m.delete()
    else:
        unauthorized_message(request, m)

    return HttpResponseRedirect(reverse("quicknote"))
