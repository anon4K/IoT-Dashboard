from django.shortcuts import render, redirect
from .models import Device, SensorData
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import SensorDataSerializer
from rest_framework import status
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout

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
def add_sensor_data(request, device_id):
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    sensor_data = SensorData(
        device=device,
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        distance=data.get('distance')
    )
    sensor_data.save()
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



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or '/'
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, "dashboard/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('/login/')
