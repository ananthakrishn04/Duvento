from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.exceptions import ValidationError
from typing import Dict, Any
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and notifications"""
    
    @staticmethod
    def get_group_name(session_id: str) -> str:
        """Get the standardized group name for a session"""
        return f"session_{session_id}"
    
    @staticmethod
    def validate_message(event_type: str, data: Dict[str, Any]) -> None:
        """Validate message format and required fields"""
        required_fields = {
            'join': ['type', 'profile'],
            'leave': ['type', 'profile'],
            'ready': ['type', 'profile', 'all_ready'],
            'start': ['type', 'start_time', 'problem'],
            'game_end': ['type', 'winner', 'leaderboard']
        }
        
        if event_type not in required_fields:
            raise ValidationError(f"Invalid event type: {event_type}")
            
        missing_fields = [field for field in required_fields[event_type] if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
    
    @staticmethod
    def notify_session_update(session_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Send a notification to all session participants"""
        try:
            # Log outgoing message
            logger.info(f"Outgoing WebSocket message - Session: {session_id}, Type: {event_type}, Data: {json.dumps(data)}")
            
            # Validate message format
            WebSocketManager.validate_message(event_type, data)
            
            # Add timestamp to message
            data['timestamp'] = datetime.now().isoformat()
            
            # Get channel layer
            channel_layer = get_channel_layer()
            group_name = WebSocketManager.get_group_name(session_id)
            
            # Send message to group
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': f'session_{event_type}',
                    'message': data
                }
            )
            
        except Exception as e:
            # Log the error but don't raise it to prevent breaking the main flow
            logger.error(f"Error sending WebSocket message: {str(e)}")
    
    @staticmethod
    def get_heartbeat_message() -> Dict[str, Any]:
        """Generate a heartbeat message"""
        return {
            'type': 'heartbeat',
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def format_error_message(error: str) -> Dict[str, Any]:
        """Format an error message for WebSocket transmission"""
        return {
            'type': 'error',
            'message': error,
            'timestamp': datetime.now().isoformat()
        } 