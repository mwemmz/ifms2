import React, { createContext, useState, useEffect } from 'react';
import authService from '../services/auth';

// Create context
const AuthContext = createContext(null);

// Custom hook - MUST be in a separate file or exported directly
export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('AuthProvider mounted');
    const checkAuth = async () => {
      const hasToken = authService.isAuthenticated();
      console.log('Token in localStorage:', hasToken);
      
      if (hasToken) {
        console.log('Token found, loading user...');
        await loadUser();
      } else {
        console.log('No token found, setting loading to false');
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  const loadUser = async () => {
    console.log('Loading user profile...');
    try {
      const userData = await authService.getProfile();
      console.log('User data loaded:', userData);
      setUser(userData);
    } catch (error) {
      console.error('Failed to load user:', error);
      if (error.response?.status === 401) {
        authService.logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    setError(null);
    try {
      console.log('Login attempt...');
      const result = await authService.login(credentials);
      console.log('Login result:', result);
      
      if (result.mfaRequired) {
        console.log('MFA required');
        return { mfaRequired: true };
      }
      
      console.log('Login successful, loading user...');
      await loadUser();
      return { success: true };
    } catch (error) {
      console.error('Login error in context:', error);
      setError(error.response?.data?.error || 'Login failed');
      throw error;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      await authService.register(userData);
      return { success: true };
    } catch (error) {
      setError(error.response?.data?.error || 'Registration failed');
      throw error;
    }
  };

  const verifyMFA = async (token) => {
    setError(null);
    try {
      await authService.verifyMFA(token);
      await loadUser();
      return { success: true };
    } catch (error) {
      setError(error.response?.data?.error || 'MFA verification failed');
      throw error;
    }
  };

  const logout = () => {
    console.log('Logging out...');
    authService.logout();
    setUser(null);
  };

  const updateProfile = async (profileData) => {
    setError(null);
    try {
      await authService.updateProfile(profileData);
      await loadUser();
      return { success: true };
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update profile');
      throw error;
    }
  };

  const setupMFA = async () => {
    setError(null);
    try {
      const result = await authService.setupMFA();
      return result;
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to setup MFA');
      throw error;
    }
  };

  const disableMFA = async () => {
    setError(null);
    try {
      await authService.disableMFA();
      await loadUser();
      return { success: true };
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to disable MFA');
      throw error;
    }
  };

  const isAuthenticated = () => {
    return authService.isAuthenticated();
  };

  const hasMFA = () => {
    return authService.hasMFA();
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    verifyMFA,
    updateProfile,
    setupMFA,
    disableMFA,
    isAuthenticated,
    hasMFA
  };

  console.log('AuthProvider state:', { 
    user: !!user, 
    loading, 
    error: !!error 
  });

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};