import React, { useEffect, useState } from 'react';
import { sessionService } from '../services/sessionService';

const SessionStatusMonitor = ({ sessionId }) => {
  const [status, setStatus] = useState({
    readyStatus: {
      allReady: false,
      readyParticipantsCount: 0,
    },
    hasStarted: false,
    hasEnded: false,
    winner: null,
    leaderboard: []
  });

  useEffect(() => {
    if (!sessionId) return;

    // Set up WebSocket listeners
    const readyStatusListener = sessionService.webSocketManager.addListener(
      'readyStatus',
      (data) => {
        setStatus(prevStatus => ({
          ...prevStatus,
          readyStatus: {
            allReady: data.allReady,
            readyParticipantsCount: data.readyParticipantsCount
          }
        }));
      }
    );

    const sessionStartListener = sessionService.webSocketManager.addListener(
      'sessionStart',
      () => {
        setStatus(prevStatus => ({
          ...prevStatus,
          hasStarted: true
        }));
      }
    );

    const sessionEndListener = sessionService.webSocketManager.addListener(
      'sessionEnd',
      (data) => {
        setStatus(prevStatus => ({
          ...prevStatus,
          hasEnded: true,
          winner: data.winner
        }));
      }
    );

    const leaderboardUpdateListener = sessionService.webSocketManager.addListener(
      'leaderboardUpdate',
      (data) => {
        setStatus(prevStatus => ({
          ...prevStatus,
          leaderboard: data
        }));
      }
    );

    // Fallback: fetch initial status if needed
    const getInitialStatus = async () => {
      try {
        const initialStatus = await sessionService.getSessionStatus(sessionId);
        setStatus(prevStatus => ({
          ...prevStatus,
          readyStatus: {
            allReady: initialStatus.allReady,
            readyParticipantsCount: initialStatus.readyParticipantsCount
          }
        }));
      } catch (error) {
        console.error('Failed to get initial session status:', error);
      }
    };

    getInitialStatus();

    // Cleanup function
    return () => {
      readyStatusListener();
      sessionStartListener();
      sessionEndListener();
      leaderboardUpdateListener();
    };
  }, [sessionId]);

  const renderParticipantStatus = () => {
    return (
      <div className="participant-status">
        <p>
          Ready participants: {status.readyStatus.readyParticipantsCount}
        </p>
        <p>
          All participants ready: {status.readyStatus.allReady ? 'Yes' : 'No'}
        </p>
      </div>
    );
  };

  const renderLeaderboard = () => {
    if (status.leaderboard.length === 0) {
      return <p>Leaderboard not available</p>;
    }

    return (
      <div className="leaderboard">
        <h3>Leaderboard</h3>
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Participant</th>
              <th>Problems Solved</th>
              <th>Time</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {status.leaderboard.map((entry, index) => (
              <tr key={entry.username}>
                <td>{index + 1}</td>
                <td>{entry.username}</td>
                <td>{entry.problems_solved}</td>
                <td>{entry.formatted_time}</td>
                <td>{entry.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderSessionStatus = () => {
    if (status.hasEnded) {
      return (
        <div className="session-ended">
          <h3>Session has ended</h3>
          {status.winner && <p>Winner: {status.winner}</p>}
          {renderLeaderboard()}
        </div>
      );
    }

    if (status.hasStarted) {
      return (
        <div className="session-in-progress">
          <h3>Session in progress</h3>
          {renderLeaderboard()}
        </div>
      );
    }

    return (
      <div className="session-waiting">
        <h3>Waiting for session to start</h3>
        {renderParticipantStatus()}
      </div>
    );
  };

  return (
    <div className="session-status-monitor">
      {renderSessionStatus()}
    </div>
  );
};

export default SessionStatusMonitor; 