import axios from 'axios';

// Use direct URL for now to avoid config issues
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class AuthService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/auth`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests if available
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token expiration
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async checkAdminExists() {
    const response = await this.api.get('/check-admin-exists');
    return response.data;
  }

  async signup(email, password) {
    const response = await this.api.post('/signup', {
      email,
      password,
    });
    return response.data;
  }

  async login(email, password) {
    const response = await this.api.post('/login', {
      email,
      password,
    });
    return response.data;
  }

  async changePassword(currentPassword, newPassword) {
    const response = await this.api.post('/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  }

  async getCurrentAdmin() {
    const response = await this.api.get('/me');
    return response.data;
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('admin_email');
  }

  isAuthenticated() {
    const token = localStorage.getItem('token');
    console.log('Checking authentication, token:', token ? 'exists' : 'not found');
    return !!token;
  }

  getAdminEmail() {
    return localStorage.getItem('admin_email');
  }
}

export const authService = new AuthService();
