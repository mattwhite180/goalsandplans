import datetime
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase

from .models import Goal, Plan, Task
from .views import data_to_json, run_jobs


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
        )
        Plan.objects.create(
            title="test plan (continuous)",
            description="This test should not create any tasks",
            goal=g,
            continuous=False,
            limit=10,
            add_count=1,
        )
        Plan.objects.create(
            title="test plan (continuous - limit)",
            description="This test should create 3 tasks",
            goal=g,
            continuous=True,
            limit=3,
            add_count=5,
        )
        Plan.objects.create(
            title="test plan (continuous - not yet time)",
            description="This test should not create any tasks",
            goal=g,
            continuous=True,
            limit=1,
            add_count=1,
            last_updated=datetime.date.today() - datetime.timedelta(days=1),
        )

    def test_sanity_check(self):
        errmsg = "if this fails, there is a syntax error in taskify, or a fatal runtime error"
        call_command("taskify")
        self.assertEqual(0, 0, errmsg)

    def test_task_limit(self):
        call_command("taskify")
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
