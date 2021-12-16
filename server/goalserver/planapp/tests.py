from django.test import RequestFactory, TestCase
from django.core.management import call_command
from .models import Goal, Plan, Task
from django.contrib.auth.models import AnonymousUser, User
from .views import run_jobs, dataToJson
from django.test import Client
import datetime


class CronTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        test_user = User.objects.create_user(username="testuser", password="1234")
        g = Goal.objects.create(
            title="test goal", description="test goal description", user=test_user
        )
        Plan.objects.create(
            title="test plan (continuous)",
            description="This test should create 1 task",
            goal=g,
            continuous=True,
            limit=1,
            add_count=1,
            add_period=1,
        )
        Plan.objects.create(
            title="test plan (continuous)",
            description="This test should not create any tasks",
            goal=g,
            continuous=False,
            limit=10,
            add_count=1,
            add_period=1,
        )
        Plan.objects.create(
            title="test plan (continuous - limit)",
            description="This test should create 3 tasks",
            goal=g,
            continuous=True,
            limit=3,
            add_count=5,
            add_period=1,
        )
        Plan.objects.create(
            title="test plan (continuous - not yet time)",
            description="This test should not create any tasks",
            goal=g,
            continuous=True,
            limit=1,
            add_count=1,
            add_period=2,
            last_updated = datetime.date.today() - datetime.timedelta(days=1)
        )

    def test_sanity_check(self):
        errmsg = "if this fails, there is a syntax error in crontask, or a fatal runtime error"
        call_command("crontask")
        self.assertEqual(0, 0, errmsg)

    def test_task_limit(self):
        call_command("crontask")
        val = Task.objects.count()
        expected = 4
        errmsg = (
            "expected "
            + str(expected)
            + " tasks, but counted "
            + str(val)
            + " tasks"
            + """
        if the number of tasks counted is over 100 then there might be an issue with the continuous flag
        if the number of tasks counted is over 1000 then the add period might not be working"""
        )
        self.assertEqual(val, expected, errmsg)

    def test_client_side(self):
        c = Client()
        response = c.post("/run_jobs/", {"username": "testuser", "password": "1234"})
        val = response.status_code
        expected = 302
        errmsg = (
            "expected a response code of '"
            + str(expected)
            + "', but got a response "
            + "code of '"
            + str(val)
            + "'"
        )
        self.assertEqual(val, expected, errmsg)
        val = Task.objects.count()
        expected = 4
        errmsg = (
            "expected "
            + str(expected)
            + " tasks, but counted "
            + str(val)
            + " tasks"
            + """
        if the number of tasks counted is over 100 then there might be an issue with the continuous flag
        if the number of tasks counted is over 1000 then the add period might not be working"""
        )
        self.assertEqual(val, expected, errmsg)
