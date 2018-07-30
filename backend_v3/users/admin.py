from django.contrib import admin
from . import models

admin.site.register(models.Position)
admin.site.register(models.Occupation)
admin.site.register(models.GlobalCoefficient)
admin.site.register(models.Coefficients)
admin.site.register(models.Bonus)
admin.site.register(models.User)
