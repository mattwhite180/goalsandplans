from django.urls import path, include
from django.contrib.auth import views as auth_views
import django.contrib.auth.urls

from . import views

urlpatterns = [
    path("accounts/create/", views.create_account, name="create"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="planapp/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path('accounts/change_password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("planapp/", views.home, name="home"),
    path("goal/<int:goal_id>/", views.goal, name="goal"),
    path("goal/<int:goal_id>/edit/", views.edit_goal, name="edit_goal"),
    path("goal/<int:goal_id>/delete/", views.delete_goal, name="delete_goal"),
    path("plan/<int:plan_id>/", views.plan, name="plan"),
    path("plan/<int:plan_id>/edit/", views.edit_plan, name="edit_plan"),
    path("plan/<int:plan_id>/delete/", views.delete_plan, name="delete_plan"),
    path("task/<int:task_id>/", views.task, name="task"),
    path("task/<int:task_id>/edit/", views.edit_task, name="edit_task"),
    path("task/<int:task_id>/delete/", views.delete_task, name="delete_task"),
    path("quick_task/", views.quick_task, name="quick_task"),
    path("minitodo/<int:mini_id>/", views.minitodo, name="minitodo"),
    path("minitodo/<int:mini_id>/edit/", views.edit_minitodo, name="edit_minitodo"),
    path(
        "minitodo/<int:mini_id>/delete/", views.delete_minitodo, name="delete_minitodo"
    ),
    path("task_todo/", views.task_todo, name="task_todo"),
    path("run_jobs/", views.run_jobs, name="run_jobs"),
    path("create_backup/", views.create_backup, name="create_backup"),
]
