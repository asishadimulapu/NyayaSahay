/**
 * Auth Modal Component with Lucide Icons
 * Sign In and Register modal with form validation
 */

import React, { useState } from 'react';
import { Scale, X, Mail, Lock, User, Eye, EyeOff, AlertCircle } from 'lucide-react';
import '../styles/auth.css';

function AuthModal({ isOpen, mode, onClose, onSubmit, onSwitchMode }) {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        confirmPassword: '',
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const isSignIn = mode === 'signin';

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (!formData.email || !formData.password) {
            setError('Please fill in all required fields');
            return;
        }

        if (!isSignIn) {
            if (!formData.name) {
                setError('Please enter your name');
                return;
            }
            if (formData.password !== formData.confirmPassword) {
                setError('Passwords do not match');
                return;
            }
            if (formData.password.length < 6) {
                setError('Password must be at least 6 characters');
                return;
            }
        }

        setIsLoading(true);
        try {
            await onSubmit(formData);
        } catch (err) {
            setError(err.message || 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="auth-overlay" onClick={onClose}>
            <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
                {/* Close Button */}
                <button className="auth-close" onClick={onClose}>
                    <X size={20} />
                </button>

                {/* Header */}
                <div className="auth-header">
                    <div className="auth-logo">
                        <Scale size={28} />
                    </div>
                    <h2>{isSignIn ? 'Welcome Back' : 'Create Account'}</h2>
                    <p>
                        {isSignIn
                            ? 'Sign in to access your legal consultation history'
                            : 'Join NyayaSahay for personalized legal guidance'
                        }
                    </p>
                </div>

                {/* Form */}
                <form className="auth-form" onSubmit={handleSubmit}>
                    {!isSignIn && (
                        <div className="form-group">
                            <label htmlFor="name">
                                <User size={16} /> Full Name
                            </label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Enter your full name"
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label htmlFor="email">
                            <Mail size={16} /> Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Enter your email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">
                            <Lock size={16} /> Password
                        </label>
                        <div className="password-input-wrapper">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter your password"
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                    </div>

                    {!isSignIn && (
                        <div className="form-group">
                            <label htmlFor="confirmPassword">
                                <Lock size={16} /> Confirm Password
                            </label>
                            <input
                                type="password"
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Confirm your password"
                            />
                        </div>
                    )}

                    {error && (
                        <div className="auth-error">
                            <AlertCircle size={16} /> {error}
                        </div>
                    )}

                    <button type="submit" className="auth-submit" disabled={isLoading}>
                        {isLoading ? 'Please wait...' : (isSignIn ? 'Sign In' : 'Create Account')}
                    </button>
                </form>

                {/* Footer */}
                <div className="auth-footer">
                    <p>
                        {isSignIn ? "Don't have an account? " : "Already have an account? "}
                        <button
                            type="button"
                            className="auth-switch"
                            onClick={() => onSwitchMode(isSignIn ? 'register' : 'signin')}
                        >
                            {isSignIn ? 'Sign Up' : 'Sign In'}
                        </button>
                    </p>
                </div>

                {/* Disclaimer */}
                <p className="auth-disclaimer">
                    By continuing, you agree to our Terms of Service and Privacy Policy
                </p>
            </div>
        </div>
    );
}

export default AuthModal;
