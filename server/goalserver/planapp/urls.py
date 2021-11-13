from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:goal_id>/', views.goal, name='goal'),
    path('<int:plan_id>/', views.plan, name='plan'),
    path('<int:task_id>/', views.task, name='task'),
]