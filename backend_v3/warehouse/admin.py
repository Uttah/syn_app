from django.contrib import admin
from . import models

admin.site.register(models.Manufacturer)
admin.site.register(models.Good)
admin.site.register(models.Unit)
admin.site.register(models.Location)
admin.site.register(models.GoodKind)
admin.site.register(models.GoodGroup)
