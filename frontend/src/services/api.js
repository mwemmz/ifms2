import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Monitor localStorage changes
const originalSetItem = localStorage.setItem;
localStorage.setItem = function(key, value) {
  if (key === 'access_token') {
    console.log('📝 TOKEN SET in localStorage:', value ? value.substring(0, 20) + '...' : 'null');
    console.trace('Token set trace:');
  }
  originalSetItem.apply(this, arguments);
};

const originalRemoveItem = localStorage.removeItem;
localStorage.removeItem = function(key) {
  if (key === 'access_token') {
    console.log('🗑️ TOKEN REMOVED from localStorage');
    console.trace('Token remove trace:');
  }
  originalRemoveItem.apply(this, arguments);
};

// Also monitor storage events from other tabs/windows
window.addEventListener('storage', (e) => {
  if (e.key === 'access_token') {
    console.log('🔄 TOKEN CHANGED in localStorage (from another tab):');
    console.log('  Old value:', e.oldValue ? 'exists' : 'none');
    console.log('  New value:', e.newValue ? 'exists' : 'none');
  }
});

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Set to false since we're using token auth
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    console.log(`🌐 REQUEST: ${config.method?.toUpperCase()} ${config.url}`);
    console.log('  Token exists in localStorage:', !!token);
    
    if (token) {
      console.log('  Adding token to Authorization header');
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log('  No token found for request');
    }
    
    // Log request data for debugging
    if (config.data) {
      console.log('  Request data:', config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ RESPONSE: ${response.status} ${response.config.url}`);
    console.log('  Response data:', response.data);
    return response;
  },
  (error) => {
    console.error('❌ Response error:', error.message);
    
    if (error.config) {
      console.error('  Failed request:', error.config.method?.toUpperCase(), error.config.url);
    }
    
    const { response } = error;
    
    if (response) {
      console.error('  Status:', response.status);
      console.error('  Status text:', response.statusText);
      console.error('  Response data:', response.data);
      
      // Handle specific status codes
      switch (response.status) {
        case 400:
          toast.error(response.data?.error || 'Bad request');
          break;
          
        case 401:
          console.log('🔐 401 Unauthorized - checking token...');
          const currentToken = localStorage.getItem('access_token');
          console.log('  Current token in localStorage:', !!currentToken);
          
          if (currentToken) {
            console.log('  Token exists but was rejected - clearing it');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            toast.error('Session expired. Please login again.');
            
            // Only redirect if not already on login page
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
          } else {
            console.log('  No token found - redirecting to login');
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
          }
          break;
          
        case 403:
          toast.error('You don\'t have permission to access this resource');
          break;
          
        case 404:
          toast.error('Resource not found');
          break;
          
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
          
        case 500:
        case 502:
        case 503:
          toast.error('Server error. Please try again later.');
          break;
          
        default:
          toast.error(response.data?.error || 'An error occurred');
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('  No response received');
      toast.error('Cannot connect to server. Please check your connection.');
    } else {
      // Something happened in setting up the request
      console.error('  Request setup error:', error.message);
      toast.error('Request failed');
    }
    
    return Promise.reject(error);
  }
);

// Add a method to check token validity
api.checkAuth = () => {
  const token = localStorage.getItem('access_token');
  console.log('🔍 Auth check - Token exists:', !!token);
  return !!token;
};

// Add a method to get current token (for debugging)
api.getTokenInfo = () => {
  const token = localStorage.getItem('access_token');
  return {
    exists: !!token,
    preview: token ? token.substring(0, 20) + '...' : null,
    length: token ? token.length : 0
  };
};

export default api;