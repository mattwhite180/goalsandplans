from django.contrib import admin

from .models import Archive, Goal, Issue, Plan, Prize, Task, TodoList, UserData

admin.site.site_url = "/"


class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "priority")


class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "id",
        "user",
        "description",
        "default_priority",
        "default_points",
        "keep_at_limit",
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    )


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "id",
        "user",
        "description",
        "priority",
        "todolist",
        "plan",
        "points",
    )


class TodoListAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "priority")


class PrizeAdmin(admin.ModelAdmin):
    list_display = ("title", "id", "user", "description", "points")


class UserDataAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "id")


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "obj_info",
        "where",
        "when",
        "exception_string",
        "ticket",
        "resolved",
    )


class ArchiveAdmin(admin.ModelAdmin):
    list_display = ("created", "title", "description")


admin.site.register(Goal, GoalAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TodoList, TodoListAdmin)
admin.site.register(Prize, PrizeAdmin)
admin.site.register(UserData, UserDataAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Archive, ArchiveAdmin)
