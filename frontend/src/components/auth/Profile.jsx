import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import profileService from '../../services/profile';
import {
  User,
  Mail,
  DollarSign,
  Target,
  Shield,
  Key,
  Smartphone,
  LogOut,
  CheckCircle,
  XCircle,
  AlertCircle,
  Copy,
  Eye,
  EyeOff,
  Lock,
  Save
} from 'lucide-react';
import './Profile.css';
import toast from 'react-hot-toast';
import QRCode from 'qrcode';

const Profile = () => {
  const { user, updateProfile: updateAuthProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [securityStatus, setSecurityStatus] = useState(null);
  const [activeSessions, setActiveSessions] = useState([]);
  const [showMFA, setShowMFA] = useState(false);
  const [mfaData, setMfaData] = useState(null);
  const [mfaToken, setMfaToken] = useState('');
  const [showMFAInput, setShowMFAInput] = useState(false);
  const [showQRCode, setShowQRCode] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [editing, setEditing] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [passwordErrors, setPasswordErrors] = useState({});
  const [formData, setFormData] = useState({
    full_name: '',
    monthly_salary: '',
    savings_goal: '',
  });

  useEffect(() => {
    loadProfileData();
    loadSecurityData();
  }, [user]);

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.profile?.full_name || '',
        monthly_salary: user.profile?.monthly_salary || '',
        savings_goal: user.profile?.savings_goal || '',
      });
    }
  }, [user]);

  const loadProfileData = async () => {
    try {
      const profile = await profileService.getProfile();
      // Update context if needed
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const loadSecurityData = async () => {
    try {
      const [status, sessions] = await Promise.all([
        profileService.getSecurityStatus(),
        profileService.getActiveSessions()
      ]);
      setSecurityStatus(status);
      setActiveSessions(sessions.sessions || []);
    } catch (error) {
      console.error('Failed to load security data:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (passwordErrors[name]) {
      setPasswordErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validatePasswordForm = () => {
    const errors = {};
    
    if (!passwordData.current_password) {
      errors.current_password = 'Current password is required';
    }
    
    if (!passwordData.new_password) {
      errors.new_password = 'New password is required';
    } else if (passwordData.new_password.length < 8) {
      errors.new_password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[A-Z])/.test(passwordData.new_password)) {
      errors.new_password = 'Password must contain at least one uppercase letter';
    } else if (!/(?=.*[0-9])/.test(passwordData.new_password)) {
      errors.new_password = 'Password must contain at least one number';
    }
    
    if (!passwordData.confirm_password) {
      errors.confirm_password = 'Please confirm your password';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
    }
    
    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      await profileService.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      toast.success('Password changed successfully!');
      setShowPasswordChange(false);
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      
      // Logout from other sessions for security
      await profileService.logoutAllSessions();
      toast.success('Logged out from other devices for security');
      
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to change password';
      toast.error(message);
      
      if (message.includes('Current password is incorrect')) {
        setPasswordErrors(prev => ({
          ...prev,
          current_password: 'Current password is incorrect'
        }));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Convert string numbers to floats
      const profileData = {
        ...formData,
        monthly_salary: formData.monthly_salary ? parseFloat(formData.monthly_salary) : 0,
        savings_goal: formData.savings_goal ? parseFloat(formData.savings_goal) : 0,
      };

      await updateAuthProfile(profileData);
      setEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSetupMFA = async () => {
    setLoading(true);
    try {
      const result = await profileService.setupMFA();
      setMfaData(result);
      
      // Generate QR code
      const qr = await QRCode.toDataURL(result.qr_code);
      setQrCodeUrl(qr);
      
      setShowMFA(true);
      setShowQRCode(true);
      toast.success('MFA setup initiated');
    } catch (error) {
      toast.error('Failed to setup MFA');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyMFA = async () => {
    if (!mfaToken || mfaToken.length !== 6) {
      toast.error('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);
    try {
      await profileService.verifyMFA(mfaToken);
      setShowMFA(false);
      setShowMFAInput(false);
      setShowQRCode(false);
      await loadSecurityData();
      await updateAuthProfile({}); // Refresh user data
      toast.success('MFA enabled successfully!');
    } catch (error) {
      toast.error('Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    if (!window.confirm('Are you sure you want to disable MFA? This will make your account less secure.')) {
      return;
    }

    setLoading(true);
    try {
      await profileService.disableMFA();
      await loadSecurityData();
      await updateAuthProfile({}); // Refresh user data
      toast.success('MFA disabled successfully');
    } catch (error) {
      toast.error('Failed to disable MFA');
    } finally {
      setLoading(false);
    }
  };

  const handleLogoutAllSessions = async () => {
    if (!window.confirm('This will log you out from all other devices. Continue?')) {
      return;
    }

    setLoading(true);
    try {
      await profileService.logoutAllSessions();
      await loadSecurityData();
      toast.success('Logged out from all other sessions');
    } catch (error) {
      toast.error('Failed to logout all sessions');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  const getSecurityScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getPasswordStrength = (password) => {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (/(?=.*[A-Z])/.test(password)) strength++;
    if (/(?=.*[0-9])/.test(password)) strength++;
    if (/(?=.*[!@#$%^&*])/.test(password)) strength++;
    
    return strength;
  };

  const passwordStrength = getPasswordStrength(passwordData.new_password);
  const strengthPercentage = (passwordStrength / 4) * 100;
  
  const getStrengthColor = () => {
    if (strengthPercentage <= 25) return '#ef4444';
    if (strengthPercentage <= 50) return '#f59e0b';
    if (strengthPercentage <= 75) return '#3b82f6';
    return '#10b981';
  };

  return (
    <div className="profile-container">
      <h1 className="page-title">Profile Settings</h1>

      <div className="profile-grid">
        {/* Personal Information */}
        <div className="profile-card">
          <div className="card-header">
            <div className="header-icon">
              <User size={24} />
            </div>
            <h2>Personal Information</h2>
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => setEditing(!editing)}
            >
              {editing ? 'Cancel' : 'Edit'}
            </button>
          </div>

          <div className="card-content">
            {editing ? (
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    name="full_name"
                    className="form-input"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Monthly Salary</label>
                  <div className="input-with-icon">
                    <DollarSign size={18} className="input-icon" />
                    <input
                      type="number"
                      name="monthly_salary"
                      className="form-input with-icon"
                      value={formData.monthly_salary}
                      onChange={handleInputChange}
                      placeholder="0.00"
                      step="0.01"
                      min="0"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Savings Goal</label>
                  <div className="input-with-icon">
                    <Target size={18} className="input-icon" />
                    <input
                      type="number"
                      name="savings_goal"
                      className="form-input with-icon"
                      value={formData.savings_goal}
                      onChange={handleInputChange}
                      placeholder="0.00"
                      step="0.01"
                      min="0"
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </form>
            ) : (
              <div className="info-display">
                <div className="info-row">
                  <span className="info-label">Username:</span>
                  <span className="info-value">{user?.username}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Email:</span>
                  <span className="info-value">{user?.email}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Full Name:</span>
                  <span className="info-value">{formData.full_name || 'Not set'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Monthly Salary:</span>
                  <span className="info-value">{formatCurrency(formData.monthly_salary)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Savings Goal:</span>
                  <span className="info-value">{formatCurrency(formData.savings_goal)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Member Since:</span>
                  <span className="info-value">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Security Status */}
        <div className="profile-card">
          <div className="card-header">
            <div className="header-icon">
              <Shield size={24} />
            </div>
            <h2>Security Status</h2>
          </div>

          <div className="card-content">
            {securityStatus && (
              <>
                <div className="security-score">
                  <div className="score-circle">
                    <svg viewBox="0 0 36 36" className="score-chart">
                      <path
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="3"
                      />
                      <path
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke={getSecurityScoreColor(securityStatus.security_score)}
                        strokeWidth="3"
                        strokeDasharray={`${securityStatus.security_score}, 100`}
                      />
                      <text x="18" y="20.35" className="score-text">
                        {securityStatus.security_score}
                      </text>
                    </svg>
                  </div>
                  <div className="score-details">
                    <div className="score-item">
                      <span>MFA Status:</span>
                      {user?.mfa_enabled ? (
                        <span className="status-badge success">
                          <CheckCircle size={14} /> Enabled
                        </span>
                      ) : (
                        <span className="status-badge warning">
                          <AlertCircle size={14} /> Disabled
                        </span>
                      )}
                    </div>
                    <div className="score-item">
                      <span>Active Sessions:</span>
                      <span>{activeSessions.length}</span>
                    </div>
                    <div className="score-item">
                      <span>Failed Logins (24h):</span>
                      <span>{securityStatus.failed_logins_24h || 0}</span>
                    </div>
                    <div className="score-item">
                      <span>Active Alerts:</span>
                      <span>{securityStatus.active_alerts || 0}</span>
                    </div>
                  </div>
                </div>

                {securityStatus.deductions?.length > 0 && (
                  <div className="security-deductions">
                    <p className="deductions-title">Security Improvements:</p>
                    <ul>
                      {securityStatus.deductions.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Password Change */}
        <div className="profile-card">
          <div className="card-header">
            <div className="header-icon">
              <Lock size={24} />
            </div>
            <h2>Password</h2>
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => setShowPasswordChange(!showPasswordChange)}
            >
              {showPasswordChange ? 'Cancel' : 'Change Password'}
            </button>
          </div>

          <div className="card-content">
            {showPasswordChange ? (
              <form onSubmit={handlePasswordSubmit}>
                <div className="form-group">
                  <label className="form-label">Current Password</label>
                  <div className="password-input-wrapper">
                    <input
                      type={showCurrentPassword ? 'text' : 'password'}
                      name="current_password"
                      className={`form-input ${passwordErrors.current_password ? 'error' : ''}`}
                      value={passwordData.current_password}
                      onChange={handlePasswordChange}
                      placeholder="Enter current password"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    >
                      {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {passwordErrors.current_password && (
                    <p className="error-message">{passwordErrors.current_password}</p>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">New Password</label>
                  <div className="password-input-wrapper">
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      name="new_password"
                      className={`form-input ${passwordErrors.new_password ? 'error' : ''}`}
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      placeholder="Enter new password"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                    >
                      {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  
                  {passwordData.new_password && (
                    <div className="password-strength">
                      <div 
                        className="strength-bar"
                        style={{
                          width: `${strengthPercentage}%`,
                          backgroundColor: getStrengthColor()
                        }}
                      />
                      <p className="strength-text">
                        Password strength: {
                          strengthPercentage <= 25 ? 'Weak' :
                          strengthPercentage <= 50 ? 'Fair' :
                          strengthPercentage <= 75 ? 'Good' : 'Strong'
                        }
                      </p>
                    </div>
                  )}
                  
                  {passwordErrors.new_password && (
                    <p className="error-message">{passwordErrors.new_password}</p>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Confirm New Password</label>
                  <div className="password-input-wrapper">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      name="confirm_password"
                      className={`form-input ${passwordErrors.confirm_password ? 'error' : ''}`}
                      value={passwordData.confirm_password}
                      onChange={handlePasswordChange}
                      placeholder="Confirm new password"
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {passwordErrors.confirm_password && (
                    <p className="error-message">{passwordErrors.confirm_password}</p>
                  )}
                </div>

                <div className="password-requirements">
                  <p className="requirements-title">Password must contain:</p>
                  <ul>
                    <li className={passwordData.new_password.length >= 8 ? 'met' : ''}>
                      ✓ At least 8 characters
                    </li>
                    <li className={/(?=.*[A-Z])/.test(passwordData.new_password) ? 'met' : ''}>
                      ✓ One uppercase letter
                    </li>
                    <li className={/(?=.*[0-9])/.test(passwordData.new_password) ? 'met' : ''}>
                      ✓ One number
                    </li>
                    <li className={/(?=.*[!@#$%^&*])/.test(passwordData.new_password) ? 'met' : ''}>
                      ✓ One special character (optional)
                    </li>
                  </ul>
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Update Password'}
                </button>
              </form>
            ) : (
              <div className="password-info">
                <p>.</p>
                <p className="last-changed">.</p>
                <p className="password-hint">
                  Password Hint: Use a strong, unique password to keep your account secure.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* MFA Settings */}
<div className="profile-card">
  <div className="card-header">
    <div className="header-icon">
      <Smartphone size={24} />
    </div>
    <h2>Two-Factor Authentication</h2>
  </div>

  <div className="card-content">
    {!showMFA ? (
      <div className="mfa-status">
        <div className="status-row">
          <span>Current Status:</span>
          {user?.mfa_enabled ? (
            <span className="status-badge success">
              <CheckCircle size={14} /> Enabled
            </span>
          ) : (
            <span className="status-badge warning">
              <AlertCircle size={14} /> Disabled
            </span>
          )}
        </div>

        {!user?.mfa_enabled ? (
          <button
            className="btn btn-primary"
            onClick={handleSetupMFA}
            disabled={loading}
          >
            <Key size={18} />
            Setup MFA
          </button>
        ) : (
          <button
            className="btn btn-danger"
            onClick={handleDisableMFA}
            disabled={loading}
          >
            Disable MFA
          </button>
        )}
      </div>
    ) : (
      <div className="mfa-setup-container">
        {showQRCode && mfaData && (
          <>
            {/* QR Code Section */}
            <div className="qr-section">
              <h3>Setup Two-Factor Authentication</h3>
              <p className="qr-description">
                Scan this QR code with Google Authenticator or enter the secret key manually
              </p>
              
              <div className="qr-code-wrapper">
                <img src={qrCodeUrl} alt="MFA QR Code" className="qr-code" />
              </div>

              {/* Manual Secret Section - UPDATED WITH FULL INSTRUCTIONS */}
              <div className="manual-secret">
                <p className="manual-secret-label">Can't scan? Enter manually:</p>
                
                {/* Step-by-step instructions */}
                <div style={{ 
                  background: '#f0f5ff', 
                  padding: '1rem', 
                  borderRadius: '0.75rem',
                  marginBottom: '1rem',
                  textAlign: 'left'
                }}>
                  <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600, color: '#1a202c' }}>
                    📱 Google Authenticator Setup:
                  </p>
                  <ol style={{ margin: 0, paddingLeft: '1.25rem', color: '#2d3748' }}>
                    <li>Tap the <strong>+</strong> button</li>
                    <li>Select <strong>"Enter a setup key"</strong></li>
                    <li>Enter these details exactly:</li>
                  </ol>
                </div>

                {/* Account name */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#f7fafc',
                  padding: '0.75rem',
                  borderRadius: '0.75rem',
                  marginBottom: '0.75rem'
                }}>
                  <span style={{ minWidth: '70px', fontWeight: 500, color: '#4a5568' }}>Account:</span>
                  <code style={{ 
                    flex: 1,
                    background: 'white',
                    padding: '0.5rem',
                    borderRadius: '0.5rem',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem'
                  }}>
                    {user?.username || 'IFMS'}
                  </code>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(user?.username || 'IFMS');
                      toast.success('Account name copied!');
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#667eea',
                      padding: '0.25rem'
                    }}
                  >
                    <Copy size={16} />
                  </button>
                </div>

                {/* Secret key - using your existing secret-code style */}
                <div style={{ marginBottom: '0.75rem' }}>
                  <div style={{ fontWeight: 500, color: '#4a5568', marginBottom: '0.5rem' }}>Secret Key:</div>
                  <div 
                    className="secret-code"
                    onClick={() => copyToClipboard(mfaData.secret)}
                    style={{ cursor: 'pointer' }}
                  >
                    <code>{mfaData.secret}</code>
                    <Copy size={14} className="copy-icon" />
                  </div>
                </div>

                {/* Type */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: '#f7fafc',
                  padding: '0.75rem',
                  borderRadius: '0.75rem'
                }}>
                  <span style={{ minWidth: '70px', fontWeight: 500, color: '#4a5568' }}>Type:</span>
                  <span style={{ color: '#2d3748' }}>Time-based</span>
                </div>

                {/* Important note */}
                <div style={{
                  marginTop: '1rem',
                  padding: '0.75rem',
                  background: '#fff3cd',
                  borderLeft: '4px solid #ffc107',
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#856404'
                }}>
                  <strong>⚠️ Important:</strong> The secret key is case-sensitive. Make sure you type it exactly as shown.
                </div>
              </div>
            </div>

            {/* Next Button */}
            {!showMFAInput && (
              <button
                className="btn btn-primary mfa-next-btn"
                onClick={() => setShowMFAInput(true)}
              >
                I've added the code to my authenticator app
              </button>
            )}
          </>
        )}

        {/* Verify Section */}
        {showMFAInput && (
          <div className="verify-section">
            <h3>Verify Code</h3>
            <p className="verify-description">
              Enter the 6-digit code from your authenticator app
            </p>
            
            <div className="verify-input-wrapper">
              <input
                type="text"
                className="verify-input"
                value={mfaToken}
                onChange={(e) => setMfaToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                maxLength="6"
                autoFocus
              />
            </div>
            
            <div className="verify-actions">
              <button
                className="btn btn-primary verify-btn"
                onClick={handleVerifyMFA}
                disabled={loading || mfaToken.length !== 6}
              >
                {loading ? 'Verifying...' : 'Verify & Enable'}
              </button>
              <button
                className="btn btn-outline cancel-btn"
                onClick={() => {
                  setShowMFA(false);
                  setShowMFAInput(false);
                  setShowQRCode(false);
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    )}
  </div>
</div>

        {/* Active Sessions */}
        <div className="profile-card">
          <div className="card-header">
            <div className="header-icon">
              <LogOut size={24} />
            </div>
            <h2>Active Sessions</h2>
            {activeSessions.length > 1 && (
              <button
                className="btn btn-outline btn-sm"
                onClick={handleLogoutAllSessions}
                disabled={loading}
              >
                Logout All
              </button>
            )}
          </div>

          <div className="card-content">
            {activeSessions.length === 0 ? (
              <p className="text-secondary">No active sessions</p>
            ) : (
              <div className="sessions-list">
                {activeSessions.map((session, index) => (
                  <div key={index} className="session-item">
                    <div className="session-info">
                      <div className="session-device">
                        {session.user_agent ? (
                          <>
                            <span className="device-name">
                              {session.user_agent.split(' ')[0]} 
                            </span>
                            <span className="device-details">
                              {session.user_agent.length > 30 
                                ? session.user_agent.substring(0, 30) + '...' 
                                : session.user_agent}
                            </span>
                          </>
                        ) : (
                          <span className="device-name">Unknown Device</span>
                        )}
                      </div>
                      <div className="session-meta">
                        <span>IP: {session.ip_address || 'Unknown'}</span>
                        <span>Last active: {new Date(session.last_activity).toLocaleString()}</span>
                      </div>
                    </div>
                    {session.is_current && (
                      <span className="current-badge">Current</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;