import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserPlus } from 'lucide-react';
import './Register.css'; // Make sure this path is correct

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error for this field
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase and number';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    const { confirmPassword, ...registrationData } = formData;
    const result = await register(registrationData);
    setLoading(false);

    if (result.success) {
      navigate('/login');
    }
  };

  // Calculate password strength
  const getPasswordStrength = () => {
    const password = formData.password;
    if (!password) return null;
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/(?=.*[A-Z])/.test(password)) strength++;
    if (/(?=.*[a-z])/.test(password)) strength++;
    if (/(?=.*[0-9])/.test(password)) strength++;
    if (/(?=.*[!@#$%^&*])/.test(password)) strength++;
    
    return strength;
  };

  const strengthPercentage = (getPasswordStrength() / 5) * 100;
  
  const getStrengthColor = () => {
    if (strengthPercentage <= 20) return '#fc8181'; // Weak - red
    if (strengthPercentage <= 40) return '#fbbf24'; // Fair - yellow
    if (strengthPercentage <= 60) return '#667eea'; // Good - blue
    if (strengthPercentage <= 80) return '#48bb78'; // Strong - green
    return '#48bb78'; // Very Strong - green
  };

  const getStrengthLabel = () => {
    if (strengthPercentage <= 20) return 'Weak';
    if (strengthPercentage <= 40) return 'Fair';
    if (strengthPercentage <= 60) return 'Good';
    if (strengthPercentage <= 80) return 'Strong';
    return 'Very Strong';
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-icon-wrapper">
          <div className="register-icon">
            <UserPlus size={40} />
          </div>
        </div>

        <h1 className="register-title">Create your account</h1>
        <p className="register-subtitle">
          Or{' '}
          <Link to="/login" className="register-link">
            sign in to existing account
          </Link>
        </p>

        <form className="register-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              className={`form-input ${errors.username ? 'error' : ''}`}
              placeholder="Choose a username"
            />
            {errors.username && <p className="error-message">{errors.username}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={`form-input ${errors.email ? 'error' : ''}`}
              placeholder="Enter your email"
            />
            {errors.email && <p className="error-message">{errors.email}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Full Name (Optional)
            </label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your full name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className={`form-input ${errors.password ? 'error' : ''}`}
              placeholder="Create a password"
            />
            
            {/* Password strength indicator */}
            {formData.password && (
              <>
                <div className="password-strength">
                  <div 
                    className="strength-bar"
                    style={{ 
                      width: `${strengthPercentage}%`,
                      backgroundColor: getStrengthColor()
                    }}
                  />
                </div>
                <p className="strength-text">
                  Password strength: {getStrengthLabel()}
                </p>
              </>
            )}
            
            {errors.password && <p className="error-message">{errors.password}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
              placeholder="Confirm your password"
            />
            {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`register-button ${loading ? 'loading' : ''}`}
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <div className="register-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="register-link">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;