import React, { useState, useEffect } from 'react';
import { Bell, Check, X, AlertCircle, Info, CheckCircle, PiggyBank, Target, TrendingUp, Trash2 } from 'lucide-react';
import notificationService from '../../services/notification';
import { useNavigate } from 'react-router-dom';
import './Notifications.css';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const navigate = useNavigate();

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    const data = await notificationService.getNotifications();
    setNotifications(data);
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    if (filter === 'read') return n.read;
    return true;
  });

  const handleMarkAsRead = async (id) => {
    await notificationService.markAsRead(id);
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const handleMarkAllAsRead = async () => {
    await notificationService.markAllAsRead();
    setNotifications(prev =>
      prev.map(n => ({ ...n, read: true }))
    );
  };

  const handleDelete = async (id) => {
    await notificationService.deleteNotification(id);
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const handleClearAll = async () => {
    await notificationService.clearAll();
    setNotifications([]);
  };

  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      handleMarkAsRead(notification.id);
    }
    if (notification.link) {
      navigate(notification.link);
    }
  };

  const getNotificationIcon = (type, iconType) => {
    const props = { size: 24 };
    
    switch (type) {
      case 'warning':
        return <AlertCircle {...props} className="notif-icon warning" />;
      case 'success':
        return <CheckCircle {...props} className="notif-icon success" />;
      case 'info':
        return <Info {...props} className="notif-icon info" />;
      default:
        switch (iconType) {
          case 'piggy':
            return <PiggyBank {...props} className="notif-icon info" />;
          case 'goal':
            return <Target {...props} className="notif-icon success" />;
          case 'trend':
            return <TrendingUp {...props} className="notif-icon info" />;
          default:
            return <Bell {...props} className="notif-icon" />;
        }
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <h1>Notifications</h1>
        <div className="notifications-stats">
          <span className="unread-badge">{unreadCount} unread</span>
          {unreadCount > 0 && (
            <button className="btn btn-outline" onClick={handleMarkAllAsRead}>
              <Check size={16} />
              Mark all as read
            </button>
          )}
          {notifications.length > 0 && (
            <button className="btn btn-outline" onClick={handleClearAll}>
              <Trash2 size={16} />
              Clear all
            </button>
          )}
        </div>
      </div>

      <div className="notifications-filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({notifications.length})
        </button>
        <button
          className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
          onClick={() => setFilter('unread')}
        >
          Unread ({unreadCount})
        </button>
        <button
          className={`filter-btn ${filter === 'read' ? 'active' : ''}`}
          onClick={() => setFilter('read')}
        >
          Read ({notifications.length - unreadCount})
        </button>
      </div>

      <div className="notifications-list">
        {filteredNotifications.length === 0 ? (
          <div className="empty-state">
            <Bell size={48} />
            <p>No notifications to show</p>
          </div>
        ) : (
          filteredNotifications.map(notification => (
            <div
              key={notification.id}
              className={`notification-card ${notification.read ? 'read' : 'unread'}`}
              onClick={() => handleNotificationClick(notification)}
            >
              <div className="notification-card-icon">
                {getNotificationIcon(notification.type, notification.icon)}
              </div>
              
              <div className="notification-card-content">
                <div className="notification-card-header">
                  <h3>{notification.title}</h3>
                  <span className="notification-time">{formatDate(notification.timestamp)}</span>
                </div>
                <p className="notification-card-message">{notification.message}</p>
                {notification.actionable && (
                  <button className="notification-card-action">
                    {notification.action}
                  </button>
                )}
              </div>

              <div className="notification-card-actions">
                {!notification.read && (
                  <button
                    className="action-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMarkAsRead(notification.id);
                    }}
                    title="Mark as read"
                  >
                    <Check size={16} />
                  </button>
                )}
                <button
                  className="action-btn delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(notification.id);
                  }}
                  title="Delete"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notifications;