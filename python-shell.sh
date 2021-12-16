echo from django.contrib.auth.models import AnonymousUser, User
echo from planapp.models import Goal, Plan, Task, MiniTodo
echo from django.core import serializers
echo from planapp.views import testJsonToData
echo import datetime
echo import json
echo '---------------------------'
docker exec -it goalsandplans_server_1 python3 manage.py shell
