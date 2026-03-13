import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import './Layout.css';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // 🚨 FIX: Don't render Layout wrapper on auth pages
  const authPaths = ['/login', '/register', '/mfa-verify'];
  if (authPaths.includes(location.pathname)) {
    // Just render the child component directly without Layout wrapper
    return <Outlet />;
  }

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="layout">
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      
      <div className="layout-main">
        <Header onMenuClick={toggleSidebar} />
        
        <main className="layout-content">
          <div className="container">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div className="layout-overlay" onClick={closeSidebar} />
      )}
    </div>
  );
};

export default Layout;