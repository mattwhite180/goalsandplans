from django.contrib import admin

from .models import Goal, Plan, Prize, Task, TodoList, UserData

admin.site.site_url = "/planapp"


class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "priority")


class PlanAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "default_priority", "default_points")


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "id",
        "user",
        "description",
        "priority",
        "todolist",
        "plan",
        "points"
    )


class TodoListAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "priority")

class PrizeAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "points")

class UserDataAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "id")


admin.site.register(Goal, GoalAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TodoList, TodoListAdmin)
admin.site.register(Prize, PrizeAdmin)
admin.site.register(UserData, UserDataAdmin)