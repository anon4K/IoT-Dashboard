from rest_framework import serializers
from .models import Device, SensorData, Command

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['id', 'device', 'temperature', 'humidity', 'distance', 'timestamp']   


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ['id', 'device', 'command', 'status', 'created_at', 'acknowledged_at']