import { authService } from './authService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const sessionService = {
  async createSession() {
    const response = await fetch(`${API_BASE_URL}/api/sessions/`, {
      method: 'POST',
      body: JSON.stringify({

      }),
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

  async joinSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/join/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to join session');
    }

    return await response.json();
  },

  async getSessionStatus(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/status/`, {
      headers: {
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to get session status');
    }

    return await response.json();
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