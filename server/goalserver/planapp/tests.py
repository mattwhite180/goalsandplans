import datetime
import unittest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase

# from selenium.webdriver.chrome.options import Options

from .models import Goal, Plan, Task
from .selenium_gp import SeleniumGP
from .views import taskify


class CronTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        test_user = User.objects.create_user(
            username="testuser",
            password="1234",
            is_staff=True,
            is_superuser=True
        )
        g = Goal.objects.create(
            title="test goal",
            description="test goal description",
            user=test_user
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
            last_updated=(
                datetime.date.today() - datetime.timedelta(days=1)
            ),
            sunday=False,
            monday=False,
            tuesday=False,
            wednesday=False,
            thursday=False,
            friday=False,
            saturday=False,
        )

    def test_sanity_check(self):
        errmsg = ("if this fails, there is a syntax "
                  "error in taskify, or a fatal runtime error"
                  )
        for p in Plan.objects.all():
            taskify(p)
        self.assertEqual(0, 0, errmsg)

    def test_task_limit(self):
        for p in Plan.objects.all():
            taskify(p)
        val = Task.objects.count()
        expected = 4
        errmsg = (
            "expected ",
            str(expected),
            " tasks, but counted ",
            str(val),
            " tasks"
        )
        self.assertEqual(val, expected, errmsg)

    def test_client_side(self):
        c = Client()
        response = c.post(
            "/run_jobs/",
            {
                "username": "testuser",
                "password": "1234"
            }
        )
        val = response.status_code
        expected = 302
        errmsg = (
            "expected a response code of '",
            str(expected),
            "', but got a response ",
            "code of '",
            str(val),
            "'"
        )
        self.assertEqual(val, expected, errmsg)
        val = Task.objects.count()
        expected = 4
        errmsg = (
            f"expected {expected} tasks, but counted {val} tasks"
            "if the number of tasks counted is over 100 "
            "then there might be an issue with the "
            "continuous flag\nif the number of tasks "
            "counted is over 1000 then the add period "
            "might not be working"
        )
        self.assertEqual(val, expected, errmsg)


class TaskExpireTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        test_user = User.objects.create_user(
            username="testuser",
            password="1234"
        )
        g = Goal.objects.create(
            title="test goal",
            description="test goal description",
            user=test_user
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
        errmsg = "Task was not created"
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
        errmsg = "Task failed to expire"


# class RemoteGoogleTestCase(unittest.TestCase):
#     # check if selenium is working
#     def setUp(self):
#         self.browser = webdriver.Remote(
#             command_executor="http://chrome:4444/wd/hub",
#             desired_capabilities=DesiredCapabilities.CHROME,
#         )
#         self.addCleanup(self.browser.quit)

#     def testPageTitle(self):
#         self.browser.get("http://www.google.com")
#         self.assertIn("Google", self.browser.title)


# class MySeleniumTests(StaticLiveServerTestCase):
#     gp_ids = {
#         "login_btn": "topbar-login",
#         "create_account_btn": "topbar-create",
#         "about_btn": "topbar-about",
#         "home_btn": "topbar-home",
#         "submit": "submit"
#     }

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.username = "testuser_selenium"
#         cls.password = "1234"
#         cls.selenium = SeleniumGP(cls.live_server_url)
#         cls.selenium.get_driver.implicitly_wait(10)
#         cls.test_user = User.objects.create_user(
#             username=cls.username,
#             password=cls.password,
#             is_staff=True,
#             is_superuser=True
#         )
#         cls.test_user.save()

#     @classmethod
#     def tearDownClass(cls):
#         # cls.selenium.quit()
#         super().tearDownClass()

#     # def setUp(self):
#     #     self.sel = SeleniumGP("http://server:8000")
#     #     self.username = "testuser_selenium"
#     #     self.password = "1234"
#     #     # if User.objects.filter(username=self.username).count() == 0:
#     #     #     self.test_user = User.objects.create_user(
#     #     #         username=self.username,
#     #     #         password=self.password,
#     #     #         is_staff=True,
#     #     #         is_superuser=True
#     #     #     )
#     #     #     self.test_user.save()
#     #     self.test_user = User.objects.create_user(
#     #         username=self.username,
#     #         password=self.password,
#     #         is_staff=True,
#     #         is_superuser=True
#     #     )
#     #     self.test_user.save()
#     #     self.user = User.objects.get(username=self.username)

#     def test_sanity_check(self):
#         self.sel.goto("http://www.google.com", no_base=True)
#         self.assertIn("Google", self.sel.get_title())

#     def test_title_page(self):
#         self.sel.goto()
#         val = self.sel.get_title()
#         expected = "GoalsAndPlans"
#         errmsg = (
#             "expected ",
#             str(expected),
#             " but got ",
#             str(val),
#             " for the title of website"
#         )
#         self.assertEqual(val, expected, errmsg)

#     # def test_login_function(self):
#     #     self.sel.goto("http://server:8000")
#     #     self.assertEqual(True, self.sel.find_element("login_btn"))
#     #     self.sel.login()
#     #     self.assertEqual(True, self.find_element("home_btn"))
