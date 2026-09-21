import React, { useState } from 'react';
import { Search, Bell, ExternalLink } from 'lucide-react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Header({ user }) {
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    axios.post('/api/method/logout')
      .then(() => {
        navigate('/login');
      })
      .catch(err => {
        console.error("Logout failed", err);
      });
  };

  const getBreadcrumbs = () => {
    const path = location.pathname;
    if (path.startsWith('/3pl/operations')) return '3PL / Operations';
    if (path.startsWith('/3pl/management')) return '3PL / Management';
    if (path.startsWith('/freight/operations')) return 'Freight Management / Operations';
    if (path.startsWith('/freight/finance')) return 'Freight Management / Finance';
    if (path.startsWith('/freight/management')) return 'Freight Management / Management';
    if (path.startsWith('/freight/transportation')) return 'Freight Management / Transportation';
    return 'Dashboard';
  };

  return (
    <div className="topbar-px">
      <div className="breadcrumbs">
        Dashboard / <strong>{getBreadcrumbs()}</strong>
      </div>
      <div className="topbar-actions">
        <div className="search-bar">
          <Search size={14} color="var(--muted)" />
          <input type="text" placeholder="Search..." />
          <span className="shortcut">⌘K</span>
        </div>
        <button className="icon-btn" style={{ marginLeft: 8 }}>
          <Bell size={20} />
          <span className="indicator"></span>
        </button>
        <div style={{ position: 'relative', marginLeft: 8 }}>
          <div 
            className="avatar" 
            onClick={() => setProfileMenuOpen(!profileMenuOpen)} 
            title="Profile"
          >
            {user ? user.charAt(0).toUpperCase() : 'U'}
          </div>
          
          {profileMenuOpen && (
            <div className="profile-dropdown">
              <div className="dropdown-header">
                Logged in as <br/>
                <strong>{user}</strong>
              </div>
              <div 
                className="dropdown-item"
                onClick={() => window.location.href = import.meta.env.DEV ? `${import.meta.env.VITE_BACKEND_URL}/app` : '/app'}
              >
                <ExternalLink size={14} /> Switch to Desk
              </div>
              <div className="dropdown-divider"></div>
              <div className="dropdown-item text-danger" onClick={handleLogout}>
                Logout
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
