import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/common/PrivateRoute';

// Layout components
import Layout from './components/layout/Layout';

// Auth pages
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import MFAVerify from './components/auth/MFAVerify';

// Main pages
import Dashboard from './components/dashboard/Dashboard';
import Transactions from './components/transactions/Transactions';
import Analysis from './components/analysis/Analysis';
import Predictions from './components/predictions/Predictions';
import Advice from './components/advice/Advice';
import Budget from './components/budget/Budget';
import Reports from './components/reports/Reports';
import Security from './components/security/Security';
import Profile from './components/auth/Profile';

// Styles
import './styles/global.css';
import './styles/fixes.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
        <Routes>
          {/* Public routes - no layout */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/mfa-verify" element={<MFAVerify />} />
          
          {/* Protected routes with layout */}
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="transactions" element={<Transactions />} />
            <Route path="analysis" element={<Analysis />} />
            <Route path="predictions" element={<Predictions />} />
            <Route path="advice" element={<Advice />} />
            <Route path="budget" element={<Budget />} />
            <Route path="reports" element={<Reports />} />
            <Route path="security" element={<Security />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;