from django.contrib import admin

from .models import Goal, Plan, Task, MiniTodo

admin.site.site_url = "/planapp"

class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description', 'priority', 'user')

class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description', 'default_priority', 'goal')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description', 'priority', 'minitodo', 'plan')

class MiniTodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'user', 'description', 'priority')

admin.site.register(Goal, GoalAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(MiniTodo, MiniTodoAdmin)

