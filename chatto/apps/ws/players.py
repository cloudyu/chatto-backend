from channels.generic.websocket import AsyncWebsocketConsumer
import json
from ..game.models import Game, Challenge

class PlayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.id = self.scope['url_route']['kwargs']['id']
        try:
            game = Game.objects.get(id=self.id, user=self.user)
        except Game.DoesNotExist:
            await self.close()
            return False
        await self.channel_layer.group_add(
            self.id,
            self.channel_name
        )
        # self.disconnect()
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.id,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.id,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def new_challenge(self, event):
        challenge = event['challenge']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new-challenge',
            'challenge': challenge
        }))

    async def update_challenge(self, event):
        challenge = event['challenge']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'update-challenge',
            'challenge': challenge
        }))

    async def delete_challenge(self, event):
        challenge = event['challenge']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'delete-challenge',
            'challenge': challenge
        }))
