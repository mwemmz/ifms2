import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  console.log('PrivateRoute - loading:', loading);
  console.log('PrivateRoute - isAuthenticated:', isAuthenticated());

  if (loading) {
    return <LoadingSpinner />;
  }

  // Check localStorage directly as a backup
  const hasToken = !!localStorage.getItem('access_token');
  console.log('PrivateRoute - hasToken in localStorage:', hasToken);

  return (isAuthenticated() || hasToken) ? children : <Navigate to="/login" />;
};

export default PrivateRoute;