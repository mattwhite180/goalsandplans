from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('goal/<int:goal_id>/', views.goal, name='goal'),
    path('plan/<int:plan_id>/', views.plan, name='plan'),
    path('task/<int:task_id>/', views.task, name='task'),
    path('login', views.loginPage, name='loginPage')
]