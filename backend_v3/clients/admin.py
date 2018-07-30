from django.contrib import admin
from . import models

admin.site.register(models.ClientKind)
admin.site.register(models.ClientRelation)
admin.site.register(models.Client)
admin.site.register(models.Contact)
admin.site.register(models.ClientHistory)
admin.site.register(models.OrganizationForm)
