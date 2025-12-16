from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link device to user
    is_armed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

class SensorData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    sensor_type = models.CharField(max_length=50, default="unknown")  # for defaults

    def __str__(self):
        return f"Data for {self.device} at {self.timestamp}"
