from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse


def index(request):
    goals_list = Goals.objects.all()
    context = {'goals': goals_list}
    return render(request, 'polls/index.html', context)

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