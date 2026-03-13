import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const ActivityMonitor = ({ timeout = 30 * 60 * 1000 }) => { // Default 30 minutes
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [showWarning, setShowWarning] = useState(false);

  // Update last activity time on user interaction
  useEffect(() => {
    const updateActivity = () => {
      setLastActivity(Date.now());
      setShowWarning(false);
    };

    // Track user activity
    window.addEventListener('mousemove', updateActivity);
    window.addEventListener('keydown', updateActivity);
    window.addEventListener('click', updateActivity);
    window.addEventListener('scroll', updateActivity);

    return () => {
      window.removeEventListener('mousemove', updateActivity);
      window.removeEventListener('keydown', updateActivity);
      window.removeEventListener('click', updateActivity);
      window.removeEventListener('scroll', updateActivity);
    };
  }, []);

  // Check for inactivity
  useEffect(() => {
    const checkInactivity = () => {
      const timeSinceLastActivity = Date.now() - lastActivity;
      const warningTime = timeout - (60 * 1000); // Show warning 1 minute before timeout

      if (timeSinceLastActivity >= timeout) {
        // Timeout reached - logout
        toast.error('Session expired due to inactivity');
        logout();
        navigate('/login');
      } else if (timeSinceLastActivity >= warningTime && !showWarning) {
        // Show warning
        setShowWarning(true);
        const secondsUntilLogout = Math.ceil((timeout - timeSinceLastActivity) / 1000);
        toast.error(
          `Your session will expire in ${secondsUntilLogout} seconds due to inactivity`,
          { duration: 10000 }
        );
      }
    };

    const interval = setInterval(checkInactivity, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, [lastActivity, timeout, logout, navigate, showWarning]);

  // Calculate time remaining (for display if needed)
  const getTimeRemaining = () => {
    const timeSinceLastActivity = Date.now() - lastActivity;
    const remaining = Math.max(0, timeout - timeSinceLastActivity);
    return Math.ceil(remaining / 1000); // Return seconds remaining
  };

  // Format time for display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // This component doesn't render anything visible
  return null;
};

export default ActivityMonitor;