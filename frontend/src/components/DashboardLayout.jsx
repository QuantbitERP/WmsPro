import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Sidebar from './Sidebar';
import Header from './Header';
import '../dashboard.css';

export default function DashboardLayout() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('/api/method/frappe.auth.get_logged_user')
      .then(res => {
        if (!res.data.message) {
          navigate('/login');
        } else {
          setUser(res.data.message);
        }
      })
      .catch(() => navigate('/login'));
  }, [navigate]);

  if (!user) return <div style={{padding: '40px'}}>Loading...</div>;

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-area">
        <Header user={user} />
        <div className="content-wrapper" style={{ padding: 0 }}>
          <Outlet />
        </div>
      </div>
    </div>
  );
}
