from django.contrib import admin
from . import models

admin.site.register(models.Report)
admin.site.register(models.Process)
admin.site.register(models.SubProcess)
admin.site.register(models.FuncRole)
admin.site.register(models.Place)

