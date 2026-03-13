import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { AlertCircle } from 'lucide-react';
import './Auth.css';

const MFAVerify = () => {
  const navigate = useNavigate();
  const { verifyMFA } = useAuth();
  const [token, setToken] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [attempts, setAttempts] = useState(0);
  const inputRefs = useRef([]);

  const handleChange = (index, value) => {
    if (value.length > 1) return; // Only allow single digit
    
    const newToken = [...token];
    newToken[index] = value;
    setToken(newToken);
    
    // Clear error when user starts typing
    if (error) setError('');
    
    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace' && !token[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, 6);
    if (/^\d+$/.test(pastedData)) {
      const newToken = [...token];
      for (let i = 0; i < pastedData.length; i++) {
        newToken[i] = pastedData[i];
      }
      setToken(newToken);
      setError('');
      
      // Focus last filled input
      const lastIndex = Math.min(pastedData.length - 1, 5);
      inputRefs.current[lastIndex].focus();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const mfaToken = token.join('');
    if (mfaToken.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await verifyMFA(mfaToken);
      navigate('/dashboard');
    } catch (error) {
      // Increment attempts
      setAttempts(prev => prev + 1);
      
      // Show specific error message
      const errorMsg = error.response?.data?.error || 'Invalid verification code';
      setError(errorMsg);
      
      // Clear inputs on error
      setToken(['', '', '', '', '', '']);
      
      // Focus first input
      inputRefs.current[0].focus();
      
      // If too many attempts, show lockout message
      if (attempts >= 2) {
        setError('Too many failed attempts. Please try again in a few minutes.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-title">Two-Factor Authentication</h1>
          <p className="auth-subtitle">
            Enter the 6-digit code from your authenticator app
          </p>
        </div>
        
        {/* Error Message - This is what was missing */}
        {error && (
          <div className="alert alert-error" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1rem',
            backgroundColor: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '0.5rem',
            color: '#991b1b',
            marginBottom: '1.5rem'
          }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="mfa-input-container">
            {token.map((digit, index) => (
              <input
                key={index}
                ref={el => inputRefs.current[index] = el}
                type="text"
                className={`mfa-input ${error ? 'error' : ''}`}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={index === 0 ? handlePaste : undefined}
                maxLength={1}
                disabled={loading}
                autoFocus={index === 0}
                style={error ? { borderColor: '#ef4444' } : {}}
              />
            ))}
          </div>
          
          {/* Resend or Help Link */}
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '1rem',
            fontSize: '0.875rem'
          }}>
            <button
              type="button"
              onClick={() => {
                setAttempts(0);
                setError('');
                toast.success('New code required from authenticator app');
              }}
              style={{
                background: 'none',
                border: 'none',
                color: '#3b82f6',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              
            </button>
          </div>
          
          <button
            type="submit"
            className="btn btn-primary auth-button"
            disabled={loading}
          >
            {loading ? 'Verifying...' : 'Verify Code'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p className="text-secondary">
            {attempts > 0 && (
              <span style={{ color: '#6b7280' }}>
                Failed attempts: {attempts}/3
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default MFAVerify;