import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import { sessionService } from '../services/sessionService';

const WaitingRoom = ({ isOpen, onClose, sessionId }) => {
  const navigate = useNavigate();
  const { setReady, startSession, isReady, isStarted, error } = useSession();
  const [opponentReady, setOpponentReady] = useState(false);
  const [copied, setCopied] = useState(false);

  // Poll for opponent's ready status
  useEffect(() => {
    let interval;
    if (isOpen && sessionId) {
      interval = setInterval(async () => {
        try {
          const data = await sessionService.getSessionStatus(sessionId);
          setOpponentReady(data.opponentReady);
          
          // If both players are ready and the game has started, navigate to editor
          if (data.isStarted) {
            navigate(`/editor?session=${sessionId}`);
          }
        } catch (error) {
          console.error('Failed to fetch session status:', error);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isOpen, sessionId, navigate]);

  const handleSetReady = async () => {
    try {
      await setReady(sessionId);
    } catch (error) {
      console.error('Failed to set ready:', error);
    }
  };

  const handleStartGame = async () => {
    try {
      await startSession(sessionId);
    } catch (error) {
      console.error('Failed to start game:', error);
    }
  };

  const handleCopySessionId = () => {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">Waiting Room</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Session ID
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={sessionId}
              readOnly
              className="flex-1 p-2 border border-gray-300 rounded-lg bg-gray-50"
            />
            <button
              onClick={handleCopySessionId}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Your Status:</span>
            <span className={`px-3 py-1 rounded-full text-sm ${
              isReady ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {isReady ? 'Ready' : 'Not Ready'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Opponent Status:</span>
            <span className={`px-3 py-1 rounded-full text-sm ${
              opponentReady ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {opponentReady ? 'Ready' : 'Not Ready'}
            </span>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <button id='ready-button'
            onClick={handleSetReady}
            disabled={isReady}
            className={`flex-1 py-2 px-4 rounded-lg font-medium ${
              isReady
                ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            Ready
          </button>
          <button
            onClick={handleStartGame}
            disabled={!isReady || !opponentReady}
            className={`flex-1 py-2 px-4 rounded-lg font-medium ${
              !isReady || !opponentReady
                ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Start Game
          </button>
        </div>
      </div>
    </div>
  );
};

export default WaitingRoom; 