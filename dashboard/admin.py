from django.contrib import admin
from . models import Device, SensorData, APIKey
# Register your models here.

admin.site.register(Device)
admin.site.register(SensorData)
admin.site.register(APIKey)