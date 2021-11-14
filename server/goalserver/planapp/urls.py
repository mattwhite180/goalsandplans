from django.urls import path, include
from django.contrib.auth import views as auth_views
import django.contrib.auth.urls

from . import views

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='planapp/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/create/', views.create_account, name='create'),
    # path('accounts/create/', auth_views.PasswordChangeView.as_view(template_name='planapp/login.html'), name='create'),
    path('home/', views.home, name='home'),
    # path('accounts/change_password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('goal/<int:goal_id>/', views.goal, name='goal'),
    path('goal/<int:goal_id>/edit', views.edit_goal, name='edit_goal'),
    path('plan/<int:plan_id>/edit', views.edit_plan, name='edit_plan'),
    path('plan/<int:plan_id>/', views.plan, name='plan'),
    path('task/<int:task_id>/', views.task, name='task'),
]