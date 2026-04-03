import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import { Lock, Mail, ArrowRight, ShieldCheck, User } from 'lucide-react';
import { motion } from 'framer-motion';
import './Login.css';

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      if (isLogin) {
        const res = await api.post('/auth/login', { email, password });
        if (res.data.success) {
          const { access_token, refresh_token, user } = res.data.data;
          login(access_token, refresh_token, user);
          navigate('/dashboard');
        }
      } else {
        const res = await api.post('/auth/register', { name, email, password });
        if (res.data.success) {
          setSuccess('Account created! You can now log in.');
          setIsLogin(true);
          setPassword('');
        }
      }
    } catch (err: any) {
        setError(err.response?.data?.message || err.response?.data?.msg || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="orb orb-primary"></div>
      <div className="orb orb-secondary"></div>

      <motion.div 
        key={isLogin ? 'login' : 'register'}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-panel login-card"
      >
        <div className="login-header">
          <div className="icon-wrapper">
            <ShieldCheck size={32} className="text-accent" />
          </div>
          <h1>{isLogin ? 'Welcome Back' : 'Create Account'}</h1>
          <p>{isLogin ? 'Sign in to your FinTrack workspace' : 'Join FinTrack today'}</p>
        </div>

        {error && <div className="error-banner">{error}</div>}
        {success && <div className="error-banner" style={{background: 'var(--status-success-bg)', color: 'var(--status-success)', borderColor: 'var(--status-success)'}}>{success}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          
          {!isLogin && (
            <div className="input-group">
              <label>Full Name</label>
              <div className="input-wrapper">
                <User className="input-icon" size={18} />
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ex. John Doe"
                  required={!isLogin}
                />
              </div>
            </div>
          )}

          <div className="input-group">
            <label>Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Ex. admin@fintrack.com"
                required
              />
            </div>
          </div>

          <div className="input-group">
            <label>Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
            <ArrowRight size={18} />
          </button>

          <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px', color: 'var(--text-secondary)' }}>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <a 
              href="#" 
              onClick={(e) => { e.preventDefault(); setIsLogin(!isLogin); setError(''); setSuccess(''); }}
              style={{ color: 'var(--accent-primary)', textDecoration: 'none', fontWeight: 600 }}
            >
              {isLogin ? "Sign Up" : "Log In"}
            </a>
          </p>
        </form>
      </motion.div>
    </div>
  );
}
