from django.contrib import admin
from .models import DayOff, Order, GradeCoefficient, SalaryPayment

admin.site.register(DayOff)
admin.site.register(Order)
admin.site.register(GradeCoefficient)
admin.site.register(SalaryPayment)