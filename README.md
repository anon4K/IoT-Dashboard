# IoT-Dashboard

# 🔐 Smart Security IoT Dashboard

A web-based IoT security dashboard built with **Django** and designed to integrate with **ESP32-based smart security devices**.

This project simulates real-time sensor monitoring, device arming/disarming, and intrusion alerts — to evolve into a fully functional physical IoT security system.



🚀 Features

- User authentication (login/logout)
- Device ownership (each user sees only their devices)
- Real-time sensor data auto-refresh
- Device arming & disarming
- Motion/proximity alert detection
- Visual alert highlighting on intrusion
- REST API endpoints for IoT devices (ESP32)



🛠️ Tech Stack
- **Backend:** Django, Django REST Framework
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Database:** SQLite (development)
- **Hardware (Planned):** ESP32, motion & distance sensors



📡 API Endpoints

| Method | Endpoint | Description |
|------|--------|------------|
| POST | `/api/device/<device_id>/data/` | Send sensor data |
| GET | `/api/device/<device_id>/data/latest/` | Fetch recent sensor data |
| POST | `/api/device/<device_id>/toggle/` | Arm / Disarm device |



⚙️ Setup Instructions

```bash
git clone https://github.com/your-username/iot-security-dashboard.git
cd iot-security-dashboard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
