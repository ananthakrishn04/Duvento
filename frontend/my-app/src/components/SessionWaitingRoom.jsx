import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { sessionService } from '../services/sessionService';
import SessionStatusMonitor from './SessionStatusMonitor';

const SessionWaitingRoom = ({ sessionId, isHost }) => {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Connect to WebSocket when component mounts
    sessionService.webSocketManager.connect(sessionId);

    // Listen for session start
    const sessionStartListener = sessionService.webSocketManager.addListener(
      'sessionStart',
      (data) => {
        navigate(`/problem-solving?sessionId=${sessionId}`);
      }
    );

    // Cleanup function
    return () => {
      sessionStartListener();
    };
  }, [sessionId, navigate]);

  const handleSetReady = async () => {
    try {
      await sessionService.setReady(sessionId);
      setIsReady(true);
    } catch (error) {
      setError('Failed to set ready status. Please try again.');
    }
  };

  const handleStartSession = async () => {
    if (!isHost) return;
    
    try {
      await sessionService.startSession(sessionId);
      // No need to navigate here as the WebSocket listener will handle it
    } catch (error) {
      setError('Failed to start session. Please try again.');
    }
  };

  const handleLeaveSession = async () => {
    try {
      await sessionService.leaveSession(sessionId);
      navigate('/');
    } catch (error) {
      setError('Failed to leave session. Please try again.');
    }
  };

  return (
    <div className="session-waiting-room">
      <h2>Session Waiting Room</h2>
      <p>Session ID: {sessionId}</p>
      
      {error && <div className="error">{error}</div>}
      
      <SessionStatusMonitor sessionId={sessionId} />
      
      <div className="actions">
        {!isReady ? (
          <button 
            className="ready-btn"
            onClick={handleSetReady}
          >
            I'm Ready
          </button>
        ) : (
          <div className="ready-status">You are ready! Waiting for others...</div>
        )}
        
        {isHost && (
          <button 
            className="start-btn"
            onClick={handleStartSession}
          >
            Start Session
          </button>
        )}
        
        <button 
          className="leave-btn"
          onClick={handleLeaveSession}
        >
          Leave Session
        </button>
      </div>
    </div>
  );
};

export default SessionWaitingRoom; 