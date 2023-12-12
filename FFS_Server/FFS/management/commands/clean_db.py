from django.core.management.base import BaseCommand
from FFS.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ConfOfFines.objects.all().delete()
        Fines.objects.all().delete()
        Breaches.objects.all().delete()
        # CustomUser.objects.all().delete()