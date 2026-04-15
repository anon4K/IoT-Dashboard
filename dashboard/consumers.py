import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]
        self.group_name = f"device_{self.device_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"[WS] Client connected to {self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"[WS] Client disconnected from {self.group_name}")

    async def receive(self, text_data):

        pass

    async def sensor_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def device_command(self, event):
        await self.send(text_data=json.dumps({
            'type': 'command',
            'command_id': event['data']['command_id'],
            'command': event['data']['command'],
        }))