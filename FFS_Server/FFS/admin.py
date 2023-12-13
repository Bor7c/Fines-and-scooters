from django.contrib import admin

from . import models


admin.site.register(models.Breaches)
admin.site.register(models.ConfOfFines)
admin.site.register(models.Fines)
admin.site.register(models.CustomUser)