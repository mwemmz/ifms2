import api from './api';
import toast from 'react-hot-toast';

class AuthService {
  async register(userData) {
    try {
      console.log('📝 Register attempt with:', { ...userData, password: '[HIDDEN]' });
      const response = await api.post('/auth/register', userData);
      console.log('✅ Register response:', response.data);
      
      if (response.data) {
        toast.success('Registration successful! Please login.');
        return response.data;
      }
    } catch (error) {
      console.error('❌ Register error:', error.response?.data || error.message);
      const message = error.response?.data?.error || 'Registration failed';
      toast.error(message);
      throw error;
    }
  }

  async login(credentials) {
    try {
      console.log('🔐 Step 1: Sending login request for:', credentials.username);
      console.log('   Password provided:', credentials.password ? '✓ Yes' : '✗ No');
      
      const response = await api.post('/auth/login', credentials);
      
      console.log('🔐 Step 2: Login response received');
      console.log('   Status:', response.status);
      console.log('   Status Text:', response.statusText);
      console.log('   Full response data:', response.data);
      
      // Check if login was successful with token
      if (response.data.access_token) {
        console.log('🔐 Step 3: Access token received ✓');
        console.log('   Token length:', response.data.access_token.length);
        console.log('   Token preview:', response.data.access_token.substring(0, 20) + '...');
        
        console.log('🔐 Step 4: Storing token in localStorage...');
        localStorage.setItem('access_token', response.data.access_token);
        
        console.log('🔐 Step 5: Verifying token was stored...');
        const storedToken = localStorage.getItem('access_token');
        console.log('   Token exists in storage:', !!storedToken);
        console.log('   Stored token preview:', storedToken ? storedToken.substring(0, 20) + '...' : 'NONE');
        
        if (response.data.user) {
          console.log('🔐 Step 6: Storing user data...');
          console.log('   User data:', response.data.user);
          localStorage.setItem('user', JSON.stringify(response.data.user));
          console.log('   User data stored ✓');
        }
        
        // Double-check everything was stored
        console.log('🔐 Step 7: Final storage check:');
        console.log('   access_token:', !!localStorage.getItem('access_token'));
        console.log('   user:', !!localStorage.getItem('user'));
        
        toast.success('Login successful!');
        return response.data;
      }
      
      // If MFA required
      if (response.data.mfa_required) {
        console.log('🔐 MFA required, storing temp token');
        console.log('   Temp token:', response.data.temp_token.substring(0, 20) + '...');
        localStorage.setItem('temp_token', response.data.temp_token);
        return { mfaRequired: true };
      }
      
      console.log('⚠️ No access token in response - unexpected response format');
      console.log('   Response data:', response.data);
      return response.data;
      
    } catch (error) {
      console.error('❌ Login error in service:');
      console.error('   Message:', error.message);
      console.error('   Response status:', error.response?.status);
      console.error('   Response data:', error.response?.data);
      console.error('   Full error object:', error);
      
      const message = error.response?.data?.error || error.message || 'Login failed';
      toast.error(message);
      throw error;
    }
  }

  async verifyMFA(token) {
    try {
      const tempToken = localStorage.getItem('temp_token');
      console.log('🔐 Verifying MFA with temp token:', !!tempToken);
      
      if (!tempToken) {
        console.error('❌ No temp token found for MFA verification');
        toast.error('MFA session expired. Please login again.');
        window.location.href = '/login';
        return;
      }
      
      const response = await api.post('/auth/verify-mfa', 
        { token },
        { headers: { Authorization: `Bearer ${tempToken}` } }
      );
      
      console.log('🔐 MFA verification response:', response.data);
      
      if (response.data.access_token) {
        console.log('🔐 MFA verification successful, storing new token');
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.removeItem('temp_token');
        
        // Get user profile
        const user = await this.getProfile();
        localStorage.setItem('user', JSON.stringify(user));
        
        toast.success('MFA verified successfully!');
        return response.data;
      }
    } catch (error) {
      console.error('❌ MFA verification error:', error.response?.data || error.message);
      const message = error.response?.data?.error || 'MFA verification failed';
      toast.error(message);
      throw error;
    }
  }

  async getProfile() {
    try {
      const token = localStorage.getItem('access_token');
      console.log('👤 Fetching profile...');
      console.log('   Token exists:', !!token);
      
      if (!token) {
        console.log('   No token found, cannot fetch profile');
        return null;
      }
      
      const response = await api.get('/auth/profile');
      console.log('👤 Profile response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to get profile:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      
      // If 401, clear invalid token
      if (error.response?.status === 401) {
        console.log('🔐 Token invalid, clearing storage');
        this.logout();
      }
      
      throw error;
    }
  }

  async updateProfile(profileData) {
    try {
      console.log('📝 Updating profile with:', profileData);
      const response = await api.put('/auth/update-profile', profileData);
      
      if (response.data) {
        console.log('✅ Profile updated, refreshing user data');
        const user = await this.getProfile();
        localStorage.setItem('user', JSON.stringify(user));
        toast.success('Profile updated successfully!');
        return response.data;
      }
    } catch (error) {
      console.error('❌ Profile update error:', error.response?.data || error.message);
      const message = error.response?.data?.error || 'Failed to update profile';
      toast.error(message);
      throw error;
    }
  }

  async setupMFA() {
    try {
      console.log('🔐 Setting up MFA...');
      const response = await api.post('/auth/setup-mfa');
      console.log('✅ MFA setup response received');
      return response.data;
    } catch (error) {
      console.error('❌ MFA setup error:', error.response?.data || error.message);
      const message = error.response?.data?.error || 'Failed to setup MFA';
      toast.error(message);
      throw error;
    }
  }

  async disableMFA() {
    try {
      console.log('🔐 Disabling MFA...');
      const response = await api.post('/auth/disable-mfa');
      console.log('✅ MFA disabled');
      toast.success('MFA disabled successfully');
      return response.data;
    } catch (error) {
      console.error('❌ MFA disable error:', error.response?.data || error.message);
      const message = error.response?.data?.error || 'Failed to disable MFA';
      toast.error(message);
      throw error;
    }
  }

  logout() {
    console.log('🚪 Logging out, clearing storage:');
    console.log('   Removing access_token:', !!localStorage.getItem('access_token'));
    console.log('   Removing user:', !!localStorage.getItem('user'));
    console.log('   Removing temp_token:', !!localStorage.getItem('temp_token'));
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('temp_token');
    
    toast.success('Logged out successfully');
    window.location.href = '/login';
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        console.log('👤 Retrieved user from storage:', user);
        return user;
      } catch (e) {
        console.error('❌ Error parsing stored user:', e);
        return null;
      }
    }
    return null;
  }

  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    console.log('🔍 Auth check - Token in storage:', !!token);
    if (token) {
      console.log('   Token preview:', token.substring(0, 20) + '...');
    }
    return !!token;
  }

  hasMFA() {
    const user = this.getCurrentUser();
    return user?.mfa_enabled || false;
  }

  // Helper method to debug auth state
  debugAuthState() {
    console.log('📊 Current Auth State:');
    console.log('   access_token:', !!localStorage.getItem('access_token'));
    console.log('   temp_token:', !!localStorage.getItem('temp_token'));
    console.log('   user:', !!localStorage.getItem('user'));
    
    const token = localStorage.getItem('access_token');
    if (token) {
      console.log('   token preview:', token.substring(0, 30) + '...');
      console.log('   token length:', token.length);
    }
    
    return {
      hasToken: !!token,
      hasUser: !!localStorage.getItem('user'),
      hasTempToken: !!localStorage.getItem('temp_token')
    };
  }
}

// Create and export a single instance
const authService = new AuthService();

// Log initial auth state on load
console.log('🚀 Auth Service initialized');
authService.debugAuthState();

export default authService;