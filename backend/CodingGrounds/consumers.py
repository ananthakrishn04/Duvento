import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import PermissionDenied
from .models import GameSession, GameParticipation, CodingProfile
from .websocket_utils import WebSocketManager
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionConsumer(AsyncWebsocketConsumer):
    """Handles WebSocket connections for game sessions"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = WebSocketManager.get_group_name(self.session_id)
        
        try:
            # Verify user is authenticated
            if not self.scope["user"].is_authenticated:
                raise PermissionDenied("User must be authenticated")
            
            # # Verify user is a participant in the session
            # if not await self.is_session_participant():
            #     raise PermissionDenied("User is not a participant in this session")
            
            # Join session group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            # Accept connection
            await self.accept()
            
            # Log successful connection
            logger.info(f"WebSocket connection established - Session: {self.session_id}, User: {self.scope['user'].username}")
            
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
            
        except Exception as e:
            logger.error(f"WebSocket connection failed - Session: {self.session_id}, Error: {str(e)}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Stop heartbeat
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()
        
        # Leave session group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        
        # Log disconnection
        logger.info(f"WebSocket disconnected - Session: {self.session_id}, Code: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Log incoming message
            logger.info(f"Incoming WebSocket message - Session: {self.session_id}, Type: {message_type}, Data: {json.dumps(data)}")
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            
        except json.JSONDecodeError:
            error_msg = "Invalid JSON format"
            logger.error(f"WebSocket message error - Session: {self.session_id}, Error: {error_msg}")
            await self.send(text_data=json.dumps(
                WebSocketManager.format_error_message(error_msg)
            ))
        except Exception as e:
            logger.error(f"WebSocket message error - Session: {self.session_id}, Error: {str(e)}")
            await self.send(text_data=json.dumps(
                WebSocketManager.format_error_message(str(e))
            ))
    
    async def send_heartbeat(self):
        """Send periodic heartbeat messages"""
        while True:
            try:
                await self.send(text_data=json.dumps(
                    WebSocketManager.get_heartbeat_message()
                ))
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error - Session: {self.session_id}, Error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    @database_sync_to_async
    def is_session_participant(self):
        """Check if user is a participant in the session"""
        try:
            session = GameSession.objects.get(id=self.session_id)
            profile = CodingProfile.objects.get(user=self.scope["user"])
            return session.participants.filter(id=profile.id).exists()
        except (GameSession.DoesNotExist, CodingProfile.DoesNotExist):
            return False
    
    # Event handlers for different message types
    async def session_join(self, event):
        logger.info(f"Processing session_join event - Session: {self.session_id}")
        await self.send(text_data=json.dumps(event['message']))
    
    async def session_leave(self, event):
        logger.info(f"Processing session_leave event - Session: {self.session_id}")
        await self.send(text_data=json.dumps(event['message']))
    
    async def session_ready(self, event):
        logger.info(f"Processing session_ready event - Session: {self.session_id}")
        await self.send(text_data=json.dumps(event['message']))
    
    async def session_start(self, event):
        logger.info(f"Processing session_start event - Session: {self.session_id}")
        await self.send(text_data=json.dumps(event['message']))
    
    async def session_end(self, event):
        logger.info(f"Processing session_end event - Session: {self.session_id}")
        await self.send(text_data=json.dumps(event['message']))
    
    async def session_error(self, event):
        logger.error(f"Processing session_error event - Session: {self.session_id}, Error: {event['message']}")
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