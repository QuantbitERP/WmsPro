import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Box, Package, Activity, ArrowRight } from 'lucide-react';

export default function Login() {
  const [usr, setUsr] = useState('');
  const [pwd, setPwd] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    axios.post('/api/method/login', { usr, pwd })
      .then(res => {
        if (res.data.message === 'Logged In') {
          navigate('/');
        }
      })
      .catch(err => {
        setError(err.response?.data?.message || 'Login failed. Please check your credentials.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="login-container">
      {/* Left side - Dark Theme */}
      <div className="login-left">
        <div className="login-left-content">
          <div className="login-brand">
            <Box size={28} color="#2563EB" />
            WMSPro
          </div>

          <div className="login-hero">
            <div className="badge-dark">
              <Package size={14} />
              Enterprise 3PL Warehouse Management
            </div>
            <h1>Automate stock slotting and 3PL billing seamlessly.</h1>
            <p>
              Manage demand requisitions, intelligent putaway strategies, pick lists, and fully automated multi-tenant customer billing — all in one integrated environment.
            </p>

            <div className="login-features">
              <div className="feature-card">
                <Package size={20} />
                <div className="ft-title">Intelligent Putaway</div>
                <div className="ft-desc">ABC Slotting & Optimization</div>
              </div>
              <div className="feature-card">
                <Activity size={20} />
                <div className="ft-title">OMS Integration</div>
                <div className="ft-desc">FIFO Order Sourcing</div>
              </div>
              <div className="feature-card">
                <Box size={20} />
                <div className="ft-title">Automated Billing</div>
                <div className="ft-desc">Daily Average & Activity-Based</div>
              </div>
            </div>
          </div>

          <div className="login-footer">
            © 2026 WMSPro. Built on the Frappe Framework.
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="login-right">
        <div className="login-form-wrapper">
          <h2>Sign in to WMSPro</h2>
          <p>Enter your ERPNext credentials to access the portal.</p>

          {error && <div className="alert danger">{error}</div>}

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email address or Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="username"
                value={usr}
                onChange={(e) => setUsr(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="••••••••"
                value={pwd}
                onChange={(e) => setPwd(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'} <ArrowRight size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
