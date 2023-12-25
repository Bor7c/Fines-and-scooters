from django.core.management import BaseCommand

from FFS.models import CustomUser


def add_users():
    # CustomUser.objects.create_user("Boric", "Boric@user.com", "123")
    # CustomUser.objects.create_user("user2", "user2@user.com", "1234")
    # CustomUser.objects.create_user("user3", "user3@user.com", "1234")
    # CustomUser.objects.create_superuser("Admin", "admin@root.com", "123")
    # CustomUser.objects.create_user("Yana", "Yana@Yana.com", "123")

    print("Пользователи созданы")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()

