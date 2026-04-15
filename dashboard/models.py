import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_armed = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    @property
    def is_online(self):
        """Device is online if it sent data in the last 60 seconds."""
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).seconds < 60


class APIKey(models.Model):                         
    device = models.OneToOneField(
        Device, on_delete=models.CASCADE, related_name='api_key'
    )
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"APIKey for {self.device}"

    @staticmethod
    def generate_key():
        return secrets.token_hex(32)   # 64-char hex string


class SensorData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    sensor_type = models.CharField(max_length=50, default="unknown")

    def __str__(self):
        return f"Data for {self.device} at {self.timestamp}"
    

class Command(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('done', 'Done'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='commands')
    command = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.command} → {self.device} [{self.status}]"