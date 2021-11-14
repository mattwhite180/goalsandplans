from django.contrib import admin

from .models import Goal, Plan, Task

admin.site.site_url = "/planapp"

class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description', 'user')

class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description', 'goal')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description', 'plan')

admin.site.register(Goal, GoalAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Task, TaskAdmin)

