import React, { createContext, useContext, useState, useEffect } from 'react';
import { sessionService } from '../services/sessionService';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [error, setError] = useState(null);

  const handleSetReady = async (sessionId) => {
    try {
      await sessionService.setReady(sessionId);
      setIsReady(true);
      setError(null);
    } catch (err) {
      setError('Failed to set ready status');
      console.error(err);
      throw err;
    }
  };

  const handleStartSession = async (sessionId) => {
    try {
      await sessionService.startSession(sessionId);
      setIsStarted(true);
      setError(null);
    } catch (err) {
      setError('Failed to start session');
      console.error(err);
      throw err;
    }
  };

  const handleLeaveSession = async (sessionId) => {
    if (!sessionId) return;

    try {
      await sessionService.leaveSession(sessionId);
      setSessionId(null);
      setIsReady(false);
      setIsStarted(false);
      setError(null);
    } catch (err) {
      setError('Failed to leave session');
      console.error(err);
      throw err;
    }
  };

  const handleSubmitSolution = async (code) => {
    try {
      const result = await sessionService.submitSolution(code);
      setError(null);
      return result;
    } catch (err) {
      setError('Failed to submit solution');
      console.error(err);
      throw err;
    }
  };

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (sessionId) {
        handleLeaveSession(sessionId);
      }
    };
  }, [sessionId]);

  const value = {
    sessionId,
    setSessionId,
    isReady,
    isStarted,
    error,
    setReady: handleSetReady,
    startSession: handleStartSession,
    leaveSession: handleLeaveSession,
    submitSolution: handleSubmitSolution,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export default SessionContext; 