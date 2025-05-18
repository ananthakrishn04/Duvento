const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const authService = {
  async login(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    localStorage.setItem('userId', data.id);
    localStorage.setItem('token', data.token);
    return data;
  },

  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    
    return await response.json();
  },

  logout() {
    localStorage.removeItem('userId');
    localStorage.removeItem('token');
  },

  getToken() {
    return localStorage.getItem('token');
  },

  getUserId() {
    return localStorage.getItem('userId');
  },

  isAuthenticated() {
    return !!this.getToken();
  }
};