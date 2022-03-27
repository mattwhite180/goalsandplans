import datetime
import unittest

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .models import Goal, Plan, Task
from .views import data_to_json, run_jobs, taskify


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
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
        Plan.objects.create(
            title="test plan (continuous)",
            description="This test should not create any tasks",
            goal=g,
            continuous=False,
            limit=10,
            add_count=10,
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
        Plan.objects.create(
            title="test plan (continuous - limit)",
            description="This test should create 3 tasks",
            goal=g,
            continuous=True,
            limit=3,
            add_count=500,
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
        Plan.objects.create(
            title="test plan (continuous - not yet time)",
            description="This test should not create any tasks",
            goal=g,
            continuous=True,
            limit=1000,
            add_count=1000,
            last_updated=datetime.date.today(),
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
        Plan.objects.create(
            title="test plan (continuous - not the right day)",
            description="This test should not create any tasks",
            goal=g,
            continuous=True,
            limit=10000,
            add_count=10000,
            last_updated=datetime.date.today() - datetime.timedelta(days=1),
            sunday=False,
            monday=False,
            tuesday=False,
            wednesday=False,
            thursday=False,
            friday=False,
            saturday=False,
        )

    def test_sanity_check(self):
        errmsg = "if this fails, there is a syntax error in taskify, or a fatal runtime error"
        for p in Plan.objects.all():
            taskify(p)
        self.assertEqual(0, 0, errmsg)

    def test_task_limit(self):
        for p in Plan.objects.all():
            taskify(p)
        val = Task.objects.count()
        expected = 4
        errmsg = (
            "expected " + str(expected) + " tasks, but counted " + str(val) + " tasks"
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

class TaskExpireTestCase(TestCase):
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
            tasks_expire=True,
            limit=1,
            add_count=1,
            sunday=True,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            saturday=True,
        )
    def test_expire(self):
        for p in Plan.objects.all():
            taskify(p)
        val = Task.objects.count()
        expected = 1
        errmsg = (
            "Task was not created"
        )
        self.assertEqual(val, expected, errmsg)
        p.sunday = False
        p.monday = False
        p.tuesday = False
        p.wednesday = False
        p.thursday = False
        p.friday = False
        p.saturday = False
        p.save()
        for p in Plan.objects.all():
            taskify(p)
        val = Task.objects.count()
        expected = 0
        errmsg = (
            "Task failed to expire"
        )


class RemoteGoogleTestCase(unittest.TestCase):
    # check if selenium is working
    def setUp(self):
        self.browser = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        self.addCleanup(self.browser.quit)

    def testPageTitle(self):
        self.browser.get("http://www.google.com")
        self.assertIn("Google", self.browser.title)


class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Remote(
            command_executor="http://chrome:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        self.addCleanup(self.browser.quit)

    def test_title_page(self):
        self.browser.get("http://server:8000")
        # driver = webdriver.Chrome(options=set_chrome_options())
        val = self.browser.title
        expected = "GoalsAndPlans"
        errmsg = (
            "expected "
            + str(expected)
            + " but got "
            + str(val)
            + " for the title of website"
        )
        self.assertEqual(val, expected, errmsg)
