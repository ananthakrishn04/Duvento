import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameSession, GameParticipation, CodingProfile

logger = logging.getLogger(__name__)

class GameSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connection attempt: {self.scope['url_route']['kwargs']}")
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'session_{self.session_id}'

        # Join session group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'session_id': self.session_id
        }))

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected from session {self.session_id} with code {close_code}")
        # Leave session group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            logger.info(f"Received message type: {message_type} with data: {data}")
            
            # Send message to session group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': f'session_{message_type}',
                    'message': data
                }
            )
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))

    # Handle message types
    async def session_user_join(self, event):
        await self.send(text_data=json.dumps(event['message']))
        
    async def session_user_leave(self, event):
        await self.send(text_data=json.dumps(event['message']))
        
    async def session_ready_status(self, event):
        await self.send(text_data=json.dumps(event['message']))
        
    async def session_start(self, event):
        await self.send(text_data=json.dumps(event['message']))
        
    async def session_submission(self, event):
        await self.send(text_data=json.dumps(event['message']))
        
    async def session_chat(self, event):
        await self.send(text_data=json.dumps(event['message']))


class SimpleTestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("Connection attempt started")
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        logger.info(f"Session ID: {self.session_id}")
        
        # Join room group
        self.room_group_name = f'test_session_{self.session_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"Accepting connection for session: {self.session_id}")
        await self.accept()
        
        # Send confirmation message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to session {self.session_id}'
        }))

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting with code: {close_code}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            # Echo the message back
            await self.send(text_data=json.dumps({
                'type': 'echo',
                'original_type': message_type,
                'content': data,
                'message': 'Echo from server'
            }))
            
            # Broadcast to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_message',
                    'message': data
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Server error: {str(e)}'
            }))

    # Broadcast message to room
    async def broadcast_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'broadcast',
            'content': message
        }))