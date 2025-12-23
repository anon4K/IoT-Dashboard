from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('api/device/<str:device_id>/data/', views.add_sensor_data, name='add_sensor_data'),
    path('api/device/<str:device_id>/data/latest/', views.get_sensor_data, name='get_sensor_data'),
    path('api/device/<str:device_id>/toggle/', views.toggle_arm, name='toggle'),
    path("login/", CustomLoginView.as_view(), name="login"),
]
