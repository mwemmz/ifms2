import api from './api';

class ProfileService {
  // Get user profile from backend
  async getProfile() {
    try {
      const response = await api.get('/auth/profile');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      throw error;
    }
  }

  // Update user profile
  async updateProfile(profileData) {
    try {
      const response = await api.put('/auth/update-profile', profileData);
      return response.data;
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw error;
    }
  }

  // Setup MFA
  async setupMFA() {
    try {
      const response = await api.post('/auth/setup-mfa');
      return response.data;
    } catch (error) {
      console.error('Failed to setup MFA:', error);
      throw error;
    }
  }

  // Verify MFA token
  async verifyMFA(token) {
    try {
      const response = await api.post('/auth/verify-mfa', { token });
      return response.data;
    } catch (error) {
      console.error('Failed to verify MFA:', error);
      throw error;
    }
  }

  // Disable MFA
  async disableMFA() {
    try {
      const response = await api.post('/auth/disable-mfa');
      return response.data;
    } catch (error) {
      console.error('Failed to disable MFA:', error);
      throw error;
    }
  }

  // Get security status
  async getSecurityStatus() {
    try {
      const response = await api.get('/security/status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch security status:', error);
      throw error;
    }
  }

  // Get active sessions
  async getActiveSessions() {
    try {
      const response = await api.get('/security/sessions');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch active sessions:', error);
      throw error;
    }
  }
   async changePassword(passwordData) {
    try {
      const response = await api.post('/api/auth/change-password', passwordData);
      return response.data;
    } catch (error) {
      console.error('Failed to change password:', error);
      throw error;
    }
  }
  // Logout all sessions
  async logoutAllSessions() {
    try {
      const response = await api.delete('/api/security/sessions/all');
      return response.data;
    } catch (error) {
      console.error('Failed to logout all sessions:', error);
      throw error;
    }
  }
}

export default new ProfileService();