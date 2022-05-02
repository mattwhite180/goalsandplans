import datetime
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "creates tasks from plans"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Before: " + str(datetime.datetime.now())
            )
        )
        time.sleep(3)
        self.stdout.write(
            self.style.SUCCESS(
                "3: " + str(datetime.datetime.now())
            )
        )
        time.sleep(2)
        self.stdout.write(
            self.style.SUCCESS(
                "2: " + str(datetime.datetime.now())
            )
        )
        time.sleep(1)
        self.stdout.write(
            self.style.SUCCESS(
                "1: " + str(datetime.datetime.now())
            )
        )

        # self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        # self.stdout.write(
        #     self.style.SUCCESS(
        #         'Successfully created "%s" tasks\n----' % created
        #     )
        # )
