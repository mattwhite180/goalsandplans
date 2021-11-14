from django.contrib import admin

from .models import Goal, Plan, Task

admin.site.site_url = "/planapp"

admin.site.register(Goal)
admin.site.register(Plan)
admin.site.register(Task)
