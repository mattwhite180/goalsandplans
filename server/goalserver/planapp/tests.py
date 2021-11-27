from django.test import TestCase
from django.core.management import call_command
from .models import Goal, Plan, Task
from django.contrib.auth.models import AnonymousUser, User


class CronTaskTestCase(TestCase):
    def setUp(self):
        user_test = User.objects.create_user(
            username='testuser',
            password='1234'
            )
        g = Goal.objects.create(
            title='test goal',
            description='test goal description',
            user = user_test
        )
        Plan.objects.create(
            title='test plan (continuous)',
            description='this should increase the task count by 5',
            goal=g,
            continuous=True,
            limit=5,
            add_count=5,
            add_period=1,
        )
        Plan.objects.create(
            title='test plan (not continuous)',
            description='this should not increase the task count',
            goal=g,
            continuous=False,
            limit=700,
            add_count=700,
            add_period=1,
        )
        Plan.objects.create(
            title='test plan (continuous outside of time)',
            description='this should not increase the task count',
            goal=g,
            continuous=True,
            limit=20000,
            add_count=20000,
            add_period=2,
        )
        p = Plan.objects.create(
            title='test plan (continuous near limit)',
            description='this should only increase the task count by 18',
            goal=g,
            continuous=True,
            limit=20,
            add_count=20,
            add_period=1,
        )
        t = Task.objects.create(
            title='task test1',
            description='see if last plan will go over the limit',
            plan = p
        )
        t = Task.objects.create(
            title='task test2',
            description='see if last plan will go over the limit',
            plan = p
        )


    def test_sanity_check(self):
        errmsg = 'if this fails, there is a syntax error in crontask, or a fatal runtime error'
        call_command('crontask')
        val = 0
        expected = 0
        self.assertEqual(val, expected, errmsg)

    def test_task_limit(self):
        call_command('crontask')
        val = Task.objects.count()
        expected = 5 + 0 + 0 + 20
        errmsg = "expected " + str(expected) + " tasks, but counted " + str(val) + " tasks" + """
        if the number of tasks counted is over 100 then there might be an issue with the continuous flag
        if the number of tasks counted is over 1000 then the add period might not be working"""
        self.assertEqual(val, expected, errmsg)
