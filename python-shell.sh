echo from django.contrib.auth.models import AnonymousUser, User
echo from planapp.models import Goal, Plan, Task
echo import datetime
echo '---------------------------'
docker exec -it goalsandplans_server_1 python3 manage.py shell
