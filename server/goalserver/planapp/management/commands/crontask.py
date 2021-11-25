from django.core.management.base import BaseCommand, CommandError
from planapp.models import Goal, Plan, Task
import datetime

class Command(BaseCommand):
    help = 'creates tasks from plans'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        created = 0
        for plan in Plan.objects.all():
            if plan.continuous:
                deltaDate = datetime.date.today() - plan.last_updated
                if deltaDate.days >= plan.add_period:
                    plan.last_updated = datetime.date.today()
                    plan.save()
                    try:
                        for i in range(plan.add_count):
                            newT = Task.objects.create(
                                title=plan.recurring_task_title,
                                description=plan.recurring_task_description,
                                priority=plan.default_priority,
                                cost=plan.default_cost,
                                plan=plan
                            )
                            newT.save()
                            created += 1
                    except:
                        raise CommandError('error running crontask.py')

            self.stdout.write(self.style.SUCCESS('Successfully created "%s" tasks' % created))