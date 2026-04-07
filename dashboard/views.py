from django.shortcuts import render, redirect
from .models import Device, SensorData, APIKey
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .authentication import APIKeyAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import SensorDataSerializer
from rest_framework import status
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class CustomLoginView(LoginView):
    template_name = "dashboard/login.html"
    authentication_form = CustomLoginForm

@login_required
@csrf_exempt
def toggle_arm(request, device_id):

    try:
        device = Device.objects.get(device_id=device_id, user=request.user)
        device.is_armed = not device.is_armed
        device.save()
        return JsonResponse({"status": "success", "armed": device.is_armed})
    except Device.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)


@api_view(['POST'])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def add_sensor_data(request, device_id):
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.auth.device != device:
        return Response({"error": "API key does not match device."}, status=status.HTTP_403_FORBIDDEN)

    from django.utils import timezone
    device.last_seen = timezone.now()
    device.save(update_fields=['last_seen'])

    data = request.data
    sensor_data = SensorData(
        device=device,
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        distance=data.get('distance'),
        sensor_type=data.get('sensor_type', 'unknown')
    )
    sensor_data.save()

    # Broadcast to WebSocket group
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'device_{device_id}',
        {
            'type': 'sensor_update',   # maps to the sensor_update method in the consumer
            'data': {
                'temperature': sensor_data.temperature,
                'humidity': sensor_data.humidity,
                'distance': sensor_data.distance,
                'sensor_type': sensor_data.sensor_type,
                'timestamp': sensor_data.timestamp.strftime('%H:%M:%S'),
            }
        }
    )

    serializer = SensorDataSerializer(sensor_data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)  


# def dashboard(request):
#     devices = Device.objects.first()
#     sensor_data = SensorData.objects.filter(device=devices).order_by('timestamp')[:50]

#     timestamps = [data.timestamp.strftime("%H:%M:%S") for data in sensor_data]
#     temperatures = [data.temperature for data in sensor_data]
#     humidities = [data.humidity for data in sensor_data]    
#     distances = [data.distance for data in sensor_data]

#     context = {
#         'device': devices,
#         'timestamps': timestamps,
#         'temperatures': temperatures,
#         'humidities': humidities,
#         'distances': distances,
#     }
#     return render(request, 'dashboard/dashboard.html', context) 

@api_view(['GET'])
def get_sensor_data(request, device_id):
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({"error": "Device not found."}, status=404)
    
    sensor_data = SensorData.objects.filter(device=device).order_by('-timestamp')[:10]
    serializer = SensorDataSerializer(sensor_data, many=True)
    return Response(serializer.data)

from django.shortcuts import render
from .models import Device, SensorData
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    devices = Device.objects.filter(user=request.user)

    device_data = []

    for device in devices:
        sensor_data = SensorData.objects.filter(
            device=device
        ).order_by('-timestamp')[:10]

        # 🚨 ALERT LOGIC (PYTHON, NOT TEMPLATE)
        alert = False
        if device.is_armed:
            for data in sensor_data:
                if data.sensor_type == "motion" or (data.distance is not None and data.distance < 50):
                    alert = True
                    break

        device_data.append({
            "device": device,
            "sensor_data": sensor_data,
            "alert": alert
        })

    return render(request, "dashboard/dashboard.html", {
        "device_data": device_data
    })



# def login_view(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             next_url = request.GET.get('next') or '/'
#             return redirect(next_url)
#     else:
#         form = AuthenticationForm()
#     return render(request, "dashboard/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('/login/')


@api_view(['POST'])
def register_device(request):
    device_id = request.data.get('device_id')
    name = request.data.get('name')
    user_id = request.data.get('user_id')  # ESP32 sends the owner's user ID

    if not device_id or not name or not user_id:
        return Response(
            {"error": "device_id, name, and user_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        device = Device.objects.get(device_id=device_id)
        return Response({
            "message": "Device already registered.",
            "device_id": device.device_id,
            "api_key": device.api_key.key
        }, status=status.HTTP_200_OK)

    except Device.DoesNotExist:
        pass

    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    device = Device.objects.create(
        device_id=device_id,
        name=name,
        user=user
    )

    key = APIKey.generate_key()
    APIKey.objects.create(device=device, key=key)

    return Response({
        "message": "Device registered successfully.",
        "device_id": device.device_id,
        "api_key": key
    }, status=status.HTTP_201_CREATED)