# from channels.generic.websocket import AsyncJsonWebsocketConsumer
#
# class UpdatesConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.channel_layer.group_add("updates", self.channel_name)
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("updates", self.channel_name)
#
#     async def send_update(self, event):
#         await self.send_json(event["data"])

import json
from channels.generic.websocket import AsyncWebsocketConsumer

# class UpdatesConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.channel_layer.group_add("updates", self.channel_name)
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("updates", self.channel_name)
#
#     async def send_update(self, event):
#         await self.send(text_data=json.dumps(event["data"]))

class UpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Обработка сообщений
        await self.send(text_data=json.dumps({
            'message': 'Received'
        }))