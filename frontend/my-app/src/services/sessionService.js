import { authService } from './authService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class SessionWebSocketManager {
  constructor() {
    this.socket = null;
    this.listeners = {
      readyStatus: [],
      sessionStart: [],
      sessionEnd: [],
      leaderboardUpdate: [],
      error: []
    };
  }

  connect(sessionId) {
    if (this.socket) {
      this.disconnect();
    }

    this.socket = new WebSocket(`ws://localhost:8000/ws/sessions/${sessionId}/`);

    this.socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);

      switch (data.type) {
        case 'ready':
          this.notifyListeners('readyStatus', {
            allReady: data.all_ready,
            readyParticipantsCount: data.ready_count || 0
          });
          break;
        case 'start':
          this.notifyListeners('sessionStart', {
            startTime: data.start_time,
            problem: data.problem
          });
          break;
        case 'session_end':
          this.notifyListeners('sessionEnd', {
            winner: data.winner,
            detail: data.detail
          });
          break;
        case 'leaderboard_status':
          this.notifyListeners('leaderboardUpdate', data.leaderboard);
          break;
        default:
          console.log('Unhandled WebSocket message type:', data.type);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.notifyListeners('error', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket connection closed');
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  addListener(type, callback) {
    if (this.listeners[type]) {
      this.listeners[type].push(callback);
      return () => this.removeListener(type, callback);
    }
    return () => {};
  }

  removeListener(type, callback) {
    if (this.listeners[type]) {
      this.listeners[type] = this.listeners[type].filter(cb => cb !== callback);
    }
  }

  notifyListeners(type, data) {
    if (this.listeners[type]) {
      this.listeners[type].forEach(callback => callback(data));
    }
  }
}

// Create a singleton instance
const webSocketManager = new SessionWebSocketManager();

export const sessionService = {
  webSocketManager,

  async createSession(sessionData) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/`, {
      method: 'POST',
      body: JSON.stringify(sessionData),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    return await response.json();
  },

  async joinSession(sessionId, accessCode = null) {
    const requestBody = accessCode ? { access_code: accessCode } : {};
    
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/join/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error('Failed to join session');
    }

    // Connect to WebSocket after successfully joining
    webSocketManager.connect(sessionId);

    return await response.json();
  },

  // This method can be used as a fallback if needed
  async getSessionStatus(sessionId) {
    // Check both conditions using the new endpoints
    const [participantsResponse, readyResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/api/sessions/${sessionId}/check_participants/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authService.getToken()}`
        }
      }),
      fetch(`${API_BASE_URL}/api/sessions/${sessionId}/check_all_ready/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${authService.getToken()}`
        }
      })
    ]);

    if (!participantsResponse.ok || !readyResponse.ok) {
      throw new Error('Failed to get session status');
    }

    const [participantsData, readyData] = await Promise.all([
      participantsResponse.json(),
      readyResponse.json()
    ]);

    return {
      hasEnoughParticipants: participantsData.has_enough_participants,
      participantsCount: participantsData.participants_count,
      allReady: readyData.all_ready,
      readyParticipantsCount: readyData.ready_participants_count
    };
  },

  async setReady(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/ready/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      },
      body: JSON.stringify({ 'id': sessionId })
    });

    if (!response.ok) {
      throw new Error('Failed to set ready status');
    }

    return await response.json();
  },

  async startSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/start/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to start session');
    }

    return await response.json();
  },

  async leaveSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/leave/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to leave session');
    }

    // Disconnect from WebSocket when leaving
    webSocketManager.disconnect();

    return await response.json();
  },

  async submitSolution(code) {
    const response = await fetch(`${API_BASE_URL}/api/solve/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      },
      body: JSON.stringify({ code })
    });

    if (!response.ok) {
      throw new Error('Failed to submit solution');
    }

    return await response.json();
  }
}; 