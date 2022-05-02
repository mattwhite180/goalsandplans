import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from planapp.models import Pic


class Command(BaseCommand):
    help = "creates mock data"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):  # noqa: C901
        pic_count = 0
        pic_list = [p.title for p in Pic.objects.all()]
        if "shopping" not in pic_list:
            shopping = Pic.objects.create(
                title="shopping",
                url="planapp/images/shopping.png",
                attr_link="https://www.flaticon.com/free-icons/shopping-cart",
                attr_title="shopping cart icons",
                attr_description=("Shopping cart icons",
                                  "created by Freepik - Flaticon"
                                  )
            )
            shopping.save()
            pic_count += 1
        if "heart" not in pic_list:
            heart = Pic.objects.create(
                title="heart",
                url="planapp/images/heart.png",
                attr_link="https://www.flaticon.com/free-icons/heart",
                attr_title="heart icons",
                attr_description="Heart icons created by Freepik - Flaticon"
            )
            heart.save()
            pic_count += 1
        if "search" not in pic_list:
            search = Pic.objects.create(
                title="search",
                url="planapp/images/search.png",
                attr_link="https://www.flaticon.com/free-icons/search",
                attr_title="search icons",
                attr_description=("Search icons created by ",
                                  "Maxim Basinski Premium - Flaticon"
                                  )
            )
            search.save()
            pic_count += 1
        if "song" not in pic_list:
            song = Pic.objects.create(
                title="song",
                url="planapp/images/song.png",
                attr_link=(
                    "https://www.flaticon.com/",
                    "free-icons/google-play-music"
                ),
                attr_title="google play music icons",
                attr_description=("Google play music icons created ",
                                  "by Pixel perfect - Flaticon"
                                  )
            )
            song.save()
            pic_count += 1
        if "star" not in pic_list:
            star = Pic.objects.create(
                title="star",
                url="planapp/images/star.png",
                attr_link="https://www.flaticon.com/free-icons/star",
                attr_title="star icons",
                attr_description=("Star icons created by ",
                                  "Pixel perfect - Flaticon"
                                  )
            )
            star.save()
            pic_count += 1
        if "question" not in pic_list:
            question = Pic.objects.create(
                title="question",
                url="planapp/images/question.png",
                attr_link="https://www.flaticon.com/free-icons/question",
                attr_title="question icons",
                attr_description="Question icons created by Freepik - Flaticon"
            )
            question.save()
            pic_count += 1
        if "tear" not in pic_list:
            tear = Pic.objects.create(
                title="tear",
                url="planapp/images/tear.png",
                attr_link="https://www.flaticon.com/free-icons/tear",
                attr_title="tear icons",
                attr_description="Tear icons created by Freepik - Flaticon"
            )
            tear.save()
            pic_count += 1
        if "dollar" not in pic_list:
            dollar = Pic.objects.create(
                title="dollar",
                url="planapp/images/dollar.png",
                attr_link="https://www.flaticon.com/free-icons/dollar-symbol",
                attr_title="dollar symbol icons",
                attr_description=("Dollar symbol icons created ",
                                  "by Good Ware - Flaticon"
                                  )
                )
            dollar.save()
            pic_count += 1
        if "check" not in pic_list:
            check = Pic.objects.create(
                title="check",
                url="planapp/images/check.png",
                attr_link="https://www.flaticon.com/free-icons/check",
                attr_title="check icons",
                attr_description="Check icons created by hqrloveq - Flaticon"
            )
            check.save()
            pic_count += 1
        if "moon" not in pic_list:
            moon = Pic.objects.create(
                title="moon",
                url="planapp/images/moon.png",
                attr_link="https://www.flaticon.com/free-icons/moon",
                attr_title="moon icons",
                attr_description="Moon icons created by Good Ware - Flaticon"
            )
            moon.save()
            pic_count += 1
        if "weight" not in pic_list:
            weight = Pic.objects.create(
                title="weight",
                url="planapp/images/weight.png",
                attr_link="https://www.flaticon.com/free-icons/fitness",
                attr_title="fitness icons",
                attr_description=("Fitness icons created ",
                                  "by Smashicons - Flaticon"
                                  )
            )
            weight.save()
            pic_count += 1
        if "work" not in pic_list:
            work = Pic.objects.create(
                title="work",
                url="planapp/images/work.png",
                attr_link="https://www.flaticon.com/free-icons/work",
                attr_title="work icons",
                attr_description="Work icons created by Freepik - Flaticon"
            )
            work.save()
            pic_count += 1
        if "mail" not in pic_list:
            mail = Pic.objects.create(
                title="mail",
                url="planapp/images/mail.png",
                attr_link="https://www.flaticon.com/free-icons/mail",
                attr_title="mail icons",
                attr_description="Mail icons created by Freepik - Flaticon"
            )
            mail.save()
            pic_count += 1
        if "message" not in pic_list:
            message = Pic.objects.create(
                title="message",
                url="planapp/images/comment.png",
                attr_link="https://www.flaticon.com/free-icons/message",
                attr_title="message icons",
                attr_description="Message icons created by apien - Flaticon"
            )
            message.save()
            pic_count += 1
        if "hourglass" not in pic_list:
            hourglass = Pic.objects.create(
                title="hourglass",
                url="planapp/images/hourglass.png",
                attr_link="https://www.flaticon.com/free-icons/hourglass",
                attr_title="hourglass icons",
                attr_description=("Hourglass icons created ",
                                  "by prettycons - Flaticon"
                                  )
            )
            hourglass.save()
            pic_count += 1
        if "x" not in pic_list:
            x = Pic.objects.create(
                title="x",
                url="planapp/images/x.png",
                attr_link="https://www.flaticon.com/free-icons/close",
                attr_title="close icons",
                attr_description=("Close icons created by ",
                                  "Pixel perfect - Flaticon"
                                  )
            )
            x.save()
            pic_count += 1
        if "todo" not in pic_list:
            todo = Pic.objects.create(
                title="todo",
                url="planapp/images/todo.png",
                attr_link="https://www.flaticon.com/free-icons/to-do",
                attr_title="close icons",
                attr_description="To do icons created by Freepik - Flaticon"
            )
            todo.save()
            pic_count += 1
        if "eye" not in pic_list:
            eye = Pic.objects.create(
                title="eye",
                url="planapp/images/eye.png",
                attr_link="https://www.flaticon.com/free-icons/eye",
                attr_title="eye icons",
                attr_description="Eye icons created by Freepik - Flaticon"
            )
            eye.save()
            pic_count += 1
        if "notebook" not in pic_list:
            notebook = Pic.objects.create(
                title="notebook",
                url="planapp/images/notebook.png",
                attr_link="https://www.flaticon.com/free-icons/notebook",
                attr_title="notebook icons",
                attr_description="Notebook icons created by Freepik - Flaticon"
            )
            notebook.save()
            pic_count += 1
        if "coffee_mug" not in pic_list:
            coffee_mug = Pic.objects.create(
                title="coffee_mug",
                url="planapp/images/coffee_mug.png",
                attr_link="https://www.flaticon.com/free-icons/food",
                attr_title="food icons",
                attr_description="Food icons created by Freepik - Flaticon"
            )
            coffee_mug.save()
            pic_count += 1
        if "coffee_cup" not in pic_list:
            coffee_cup = Pic.objects.create(
                title="coffee_cup",
                url="planapp/images/coffee_cup.png",
                attr_link="https://www.flaticon.com/free-icons/food",
                attr_title="food icons",
                attr_description="Coffee icons created by Freepik - Flaticon"
            )
            coffee_cup.save()
            pic_count += 1
        if "tea" not in pic_list:
            tea = Pic.objects.create(
                title="tea",
                url="planapp/images/tea.png",
                attr_link="https://www.flaticon.com/free-icons/food",
                attr_title="tea icons",
                attr_description="Tea icons created by Freepik - Flaticon"
            )
            tea.save()
            pic_count += 1

        self.stdout.write(self.style.SUCCESS(str(datetime.datetime.now())))
        self.stdout.write(self.style.SUCCESS(f"created { pic_count } pic(s)"))
