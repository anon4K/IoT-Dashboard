from rest_framework import serializers
from .models import Device, SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['id', 'device', 'temperature', 'humidity', 'distance', 'timestamp']   

        