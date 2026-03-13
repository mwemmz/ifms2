import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Wallet,
  PieChart,
  TrendingUp,
  Lightbulb,
  Target,
  FileText,
  User,
  LogOut,
  Bell, // Add this if you want notifications in sidebar
  X
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/transactions', icon: Wallet, label: 'Transactions' },
    { path: '/analysis', icon: PieChart, label: 'Analysis' },
    { path: '/predictions', icon: TrendingUp, label: 'Predictions' },
    { path: '/advice', icon: Lightbulb, label: 'Financial Advice' },
    { path: '/budget', icon: Target, label: 'Budget Planner' },
    { path: '/reports', icon: FileText, label: 'Reports' },
    // { path: '/notifications', icon: Bell, label: 'Notifications' }, // Uncomment if you want notifications in sidebar
    { path: '/profile', icon: User, label: 'Profile' },
    // Security removed from sidebar - now accessible via Profile dropdown
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Mobile close button */}
      {isOpen && (
        <button className="sidebar-close" onClick={onClose}>
          <X size={24} />
        </button>
      )}

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <Wallet size={32} className="logo-icon" />
            <span className="logo-text">IFMS</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-link ${isActive ? 'active' : ''}`
              }
              onClick={onClose}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          {user && (
            <div className="user-info">
              <div className="user-avatar">
                {user.username?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="user-details">
                <p className="user-name">{user.username}</p>
                <p className="user-email">{user.email}</p>
              </div>
            </div>
          )}
          
          <button onClick={handleLogout} className="logout-button">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;