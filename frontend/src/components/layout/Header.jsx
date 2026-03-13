import React, { useState, useEffect, useRef } from 'react';
import { Menu, Bell, User, Check, X, AlertCircle, Info, CheckCircle, PiggyBank, Target, TrendingUp, LogOut, Settings } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import notificationService from '../../services/notification';
import './Header.css';

const Header = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const notificationRef = useRef(null);
  const userMenuRef = useRef(null);

  useEffect(() => {
    loadNotifications();
    
    // Set up interval to check for new notifications (every 5 minutes)
    const interval = setInterval(loadNotifications, 5 * 60 * 1000);
    
    // Click outside to close
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      clearInterval(interval);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const handleNotificationClick = (notification) => {
    // Mark as read
    if (!notification.read) {
      notificationService.markAsRead(notification.id);
      setNotifications(prev =>
        prev.map(n =>
          n.id === notification.id ? { ...n, read: true } : n
        )
      );
    }
    
    // Navigate if there's a link
    if (notification.link) {
      navigate(notification.link);
      setShowNotifications(false);
    }
  };

  const handleMarkAllAsRead = async () => {
    await notificationService.markAllAsRead();
    setNotifications(prev =>
      prev.map(n => ({ ...n, read: true }))
    );
  };

  const handleClearAll = async () => {
    await notificationService.clearAll();
    setNotifications([]);
    setShowNotifications(false);
  };

  const handleDeleteNotification = async (e, notificationId) => {
    e.stopPropagation();
    await notificationService.deleteNotification(notificationId);
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  const getNotificationIcon = (type, iconType) => {
    const iconProps = { size: 20 };
    
    switch (type) {
      case 'warning':
        return <AlertCircle {...iconProps} className="notification-icon warning" />;
      case 'success':
        return <CheckCircle {...iconProps} className="notification-icon success" />;
      case 'info':
        return <Info {...iconProps} className="notification-icon info" />;
      default:
        switch (iconType) {
          case 'piggy':
            return <PiggyBank {...iconProps} className="notification-icon info" />;
          case 'goal':
            return <Target {...iconProps} className="notification-icon success" />;
          case 'trend':
            return <TrendingUp {...iconProps} className="notification-icon info" />;
          default:
            return <Info {...iconProps} className="notification-icon info" />;
        }
    }
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const notifDate = new Date(timestamp);
    const diffMs = now - notifDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    return `${diffDays}d ago`;
  };

  return (
    <header className="header">
      <button className="menu-button" onClick={onMenuClick}>
        <Menu size={24} />
      </button>

      <div className="header-right">
        {/* Notifications */}
        <div className="notification-wrapper" ref={notificationRef}>
          <button 
            className={`notification-button ${showNotifications ? 'active' : ''}`}
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="notification-badge">{unreadCount}</span>
            )}
          </button>

          {showNotifications && (
            <div className="notification-dropdown">
              <div className="notification-header">
                <h3>Notifications</h3>
                <div className="notification-actions">
                  {unreadCount > 0 && (
                    <button 
                      className="notification-action"
                      onClick={handleMarkAllAsRead}
                      title="Mark all as read"
                    >
                      <Check size={16} />
                    </button>
                  )}
                  {notifications.length > 0 && (
                    <button 
                      className="notification-action"
                      onClick={handleClearAll}
                      title="Clear all"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              </div>

              <div className="notification-list">
                {notifications.length === 0 ? (
                  <div className="notification-empty">
                    <Bell size={32} />
                    <p>No notifications</p>
                  </div>
                ) : (
                  notifications.map(notification => (
                    <div
                      key={notification.id}
                      className={`notification-item ${notification.read ? 'read' : 'unread'}`}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <div className="notification-icon-wrapper">
                        {getNotificationIcon(notification.type, notification.icon)}
                      </div>
                      <div className="notification-content">
                        <div className="notification-title-row">
                          <h4>{notification.title}</h4>
                          <span className="notification-time">
                            {formatTimestamp(notification.timestamp)}
                          </span>
                        </div>
                        <p className="notification-message">{notification.message}</p>
                        {notification.actionable && (
                          <button className="notification-action-button">
                            {notification.action}
                          </button>
                        )}
                      </div>
                      <button
                        className="notification-delete"
                        onClick={(e) => handleDeleteNotification(e, notification.id)}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))
                )}
              </div>

              {notifications.length > 0 && (
                <div className="notification-footer">
                  <button 
                    className="view-all-button"
                    onClick={() => {
                      setShowNotifications(false);
                      // Navigate to a notifications page if you have one
                    }}
                  >
                    View All
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="user-menu-wrapper" ref={userMenuRef}>
          <button 
            className="user-menu-button"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <div className="user-avatar-small">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
          </button>

          {showUserMenu && (
            <div className="user-dropdown">
              <div className="user-dropdown-header">
                <div className="user-dropdown-avatar">
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="user-dropdown-info">
                  <p className="user-dropdown-name">{user?.username}</p>
                  <p className="user-dropdown-email">{user?.email}</p>
                </div>
              </div>

              <div className="user-dropdown-menu">
                <button 
                  className="user-dropdown-item"
                  onClick={() => {
                    navigate('/profile');
                    setShowUserMenu(false);
                  }}
                >
                  <User size={16} />
                  <span>Profile</span>
                </button>
                
                <button 
                  className="user-dropdown-item"
                  onClick={() => {
                    navigate('/security');
                    setShowUserMenu(false);
                  }}
                >
                  <Settings size={16} />
                  <span>Security</span>
                </button>
                
                <div className="user-dropdown-divider"></div>
                
                <button 
                  className="user-dropdown-item logout"
                  onClick={() => {
                    logout();
                    setShowUserMenu(false);
                  }}
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;