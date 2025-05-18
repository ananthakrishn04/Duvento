import { authService } from './authService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const problemService = {
  async createProblem(problemData) {
    const response = await fetch(`${API_BASE_URL}/api/problems/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      },
      body: JSON.stringify(problemData)
    });

    if (!response.ok) {
      throw new Error('Failed to create problem');
    }

    return await response.json();
  },

  async getProblems() {
    const response = await fetch(`${API_BASE_URL}/api/problems/`, {
      headers: {
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch problems');
    }

    return await response.json();
  },

  async getProblem(id) {
    const response = await fetch(`${API_BASE_URL}/api/problems/${id}/`, {
      headers: {
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch problem');
    }

    return await response.json();
  },

  async updateProblem(id, problemData) {
    const response = await fetch(`${API_BASE_URL}/api/problems/${id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authService.getToken()}`
      },
      body: JSON.stringify(problemData)
    });

    if (!response.ok) {
      throw new Error('Failed to update problem');
    }

    return await response.json();
  },

  async deleteProblem(id) {
    const response = await fetch(`${API_BASE_URL}/api/problems/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Token ${authService.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to delete problem');
    }

    return true;
  }
}; 