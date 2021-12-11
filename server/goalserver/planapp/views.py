from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Goal, Plan, Task, MiniTodo
from django.contrib.auth import authenticate, login
from .forms import GoalForm, PlanForm, TaskForm, QuickTaskForm, MiniTodoForm
from django.core.management import call_command
from django.contrib import messages
import json
import re

"""
#####
Helpful functions used by views
"""


def dataToJson():
    dataList = list()
    for g in Goal.objects.all():
        dataList.append(
            {
                "goal": {
                    "title": g.title,
                    "description": g.description,
                    "priority": g.priority,
                    "user": g.user.username,
                }
            }
        )
    for p in Plan.objects.all():
        dataList.append(
            {
                "plan": {
                    "title": p.title,
                    "description": p.description,
                    "priority": p.default_priority,
                    "goal": p.goal.title,
                    "continuous": str(p.continuous),
                    "limit": str(p.limit),
                    "default_priority": p.default_priority,
                    "add_period": str(p.add_period),
                    "recurring_task_title": p.recurring_task_title,
                    "recurring_task_description": p.recurring_task_description,
                }
            }
        )
    for t in Task.objects.all():
        if t.minitodo:
            minititle = t.minitodo.title
        else:
            minititle = ""
        dataList.append(
            {
                "task": {
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "plan": t.plan.title,
                    "minitodo": minititle,
                }
            }
        )

    for m in MiniTodo.objects.all():
        dataList.append(
            {
                "minitodo": {
                    "title": m.title,
                    "description": m.description,
                    "priority": m.priority,
                    "user": m.user.username,
                }
            }
        )
    return json.dumps(dataList)


def mobile(request):
    # Return True if the request comes from a mobile device.

    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META["HTTP_USER_AGENT"]):
        return True
    else:
        return False


def create_backup(request):
    if request.user.is_superuser or request.user.is_staff:
        context = {}
        context["is_mobile"] = mobile(request)
        context["data"] = dataToJson()
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
            errorList.append(error["message"])
    errorList.sort()
    return errorList


"""
#####
Non-model views
"""


def create_account(request):
    context = dict()

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
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/createaccount.html", context)


def run_jobs(request):
    call_command("crontask")
    messages.success(request, "ran cron task")
    return redirect("home")


def handler404(request, exception=None):
    return HttpResponseRedirect(reverse("home"))


def index(request):
    context = {}

    context["is_mobile"] = mobile(request)
    return render(request, "planapp/index.html", context)


def home(request):
    context = {}

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
    goals_list = Goal.objects.filter(user=request.user).order_by("-priority")
    context["goals_list"] = goals_list
    context["is_mobile"] = mobile(request)

    return render(request, "planapp/home.html", context)


"""
#####
Goal Views
"""


@login_required
def goal(request, goal_id):
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)

    if not userOwnsGoal(request.user, g):
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

    plan_list = Plan.objects.filter(goal=g).order_by("-default_priority")
    context = {
        "goal": g,
        "plan_list": plan_list,
        "todo": g.pull_report(),
        "form": form,
        "is_mobile": mobile(request),
    }
    return render(request, "planapp/goal.html", context)


@login_required
def edit_goal(request, goal_id):
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)

    if not userOwnsGoal(request.user, g):
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
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/formedit.html", context)
    # return HttpResponseRedirect(reverse(home))


@login_required
def delete_goal(request, goal_id):
    context = {}

    g = get_object_or_404(Goal, pk=goal_id)

    if userOwnsGoal(request.user, g):
        for p in Plan.objects.filter(goal=g):
            messages.warning(request, message_generator("deleted", p))
            for t in Task.objects.filter(plan=p):
                messages.warning(request, message_generator("deleted", t))
        messages.warning(request, message_generator("deleted", g))
        g.delete()

    context["is_mobile"] = mobile(request)
    return HttpResponseRedirect(reverse("home"))


"""
#####
Plan Views
"""


@login_required
def plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)

    if not userOwnsPlan(request.user, p):
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
        form.fields["minitodo"].queryset = MiniTodo.objects.filter(user=request.user)

    task_list = Task.objects.filter(plan=p).order_by("-priority")
    context = {
        "plan": p,
        "task_list": task_list,
        "form": form,
        "is_mobile": mobile(request),
    }
    return render(request, "planapp/plan.html", context)


@login_required
def edit_plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)

    if not userOwnsPlan(request.user, p):
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
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_plan(request, plan_id):
    context = {}

    p = get_object_or_404(Plan, pk=plan_id)
    goal_id = p.goal.id

    if userOwnsPlan(request.user, p):
        for t in Task.objects.filter(plan=p):
            messages.warning(request, message_generator("deleted", t))
        messages.warning(request, message_generator("deleted", p))
        p.delete()

    context["is_mobile"] = mobile(request)
    return HttpResponseRedirect(reverse("goal", args=(goal_id,)))


"""
#####
Task Views
"""


@login_required
def task(request, task_id):
    context = {}

    t = get_object_or_404(Task, pk=task_id)

    if not userOwnsTask(request.user, t):
        return HttpResponseRedirect(reverse("home"))

    context = {"task": t}
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/task.html", context)


@login_required
def edit_task(request, task_id):
    context = {}

    t = get_object_or_404(Task, pk=task_id)

    if not userOwnsTask(request.user, t):
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
        form.fields["minitodo"].queryset = MiniTodo.objects.filter(user=request.user)

    context["form"] = form
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_task(request, task_id):

    context = {}

    t = get_object_or_404(Task, pk=task_id)
    plan_id = t.plan.id

    if userOwnsTask(request.user, t):
        messages.warning(request, message_generator("deleted", t))
        t.delete()

    context["is_mobile"] = mobile(request)
    return HttpResponseRedirect(reverse("plan", args=(plan_id,)))


@login_required
def quick_task(request):
    context = {}

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
        form.fields["plan"].queryset = Plan.objects.filter(goal__in=goal_list)
        form.fields["minitodo"].queryset = MiniTodo.objects.filter(user=request.user)

    context["form"] = form
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/formedit.html", context)


"""
#####
MiniTodo Views
"""


@login_required
def task_todo(request):
    context = {}

    if request.method == "POST":

        form = MiniTodoForm(request.POST, use_required_attribute=False)

        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.success(request, message_generator("created", m))

    else:
        form = MiniTodoForm()

    goal_list = Goal.objects.filter(user=request.user)
    plan_list = Plan.objects.filter(goal__in=goal_list)
    task_list = Task.objects.filter(plan__in=plan_list).order_by("-priority")

    context = {
        "task_list": task_list,
        "form": form,
        "minitodo_list": MiniTodo.objects.filter(user=request.user).order_by(
            "-priority"
        ),
    }

    context["is_mobile"] = mobile(request)
    return render(request, "planapp/todo.html", context)


@login_required
def minitodo(request, mini_id):
    context = {}

    m = get_object_or_404(MiniTodo, pk=mini_id)

    if m.user.id != request.user.id:
        return HttpResponseRedirect(reverse("home"))

    task_list = Task.objects.filter(minitodo=m).order_by("-priority")
    context = {"minitodo": m, "task_list": task_list, "is_mobile": mobile(request)}
    return render(request, "planapp/minitodo.html", context)


@login_required
def edit_minitodo(request, mini_id):
    context = {}

    m = get_object_or_404(MiniTodo, pk=mini_id)

    if request.user.id != m.user.id:
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        # form = GoalForm(request.POST or None, request.FILES or None)
        form = MiniTodoForm(request.POST, instance=m)

        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.info(request, message_generator("edited", m))
            return HttpResponseRedirect(reverse("minitodo", args=(mini_id,)))
        else:
            context["error_list"] = get_errors(form)

    else:
        form = TaskForm(instance=m)

    context["form"] = form
    context["is_mobile"] = mobile(request)
    return render(request, "planapp/formedit.html", context)


@login_required
def delete_minitodo(request, mini_id):

    context = {}

    m = get_object_or_404(MiniTodo, pk=mini_id)

    if request.user.id == m.user.id:
        messages.warning(request, message_generator("deleted", m))
        m.delete()

    return HttpResponseRedirect(reverse("task_todo"))
