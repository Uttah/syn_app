from django.contrib import admin
from .models import LogisticsRequest, LogisticsTask, LogisticsRequestPosition, TransferRequest, TransferPosition

admin.site.register(LogisticsRequest)
admin.site.register(LogisticsTask)
admin.site.register(LogisticsRequestPosition)
admin.site.register(TransferRequest)
admin.site.register(TransferPosition)
