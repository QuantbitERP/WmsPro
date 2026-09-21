import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Box, Truck, ChevronDown, ChevronRight, LayoutDashboard, Briefcase, Activity, Car } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();
  const [expandedMenu, setExpandedMenu] = useState(
    location.pathname.startsWith('/3pl') ? '3pl' : location.pathname.startsWith('/freight') ? 'freight' : location.pathname.startsWith('/fleet') ? 'fleet' : null
  );

  const toggleMenu = (menu) => {
    setExpandedMenu(expandedMenu === menu ? null : menu);
  };

  return (
    <div className="sidebar-px">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <Box size={24} color="#2563EB" />
          WMSPro
        </div>
      </div>
      
      <div className="sidebar-content">
        <div className="nav-section">
          <div className="nav-label">Main Menu</div>
          
          {/* 3PL Menu */}
          <div 
            className="nav-item" 
            onClick={() => toggleMenu('3pl')}
            style={{ marginBottom: expandedMenu === '3pl' ? 4 : 8 }}
          >
            <div className="nav-item-left">
              <Box size={18} /> 3PL
            </div>
            {expandedMenu === '3pl' ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>
          
          {expandedMenu === '3pl' && (
            <div style={{ paddingLeft: 12, marginBottom: 12 }}>
              <NavLink 
                to="/3pl/operations" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <LayoutDashboard size={16} /> Operations
                </div>
              </NavLink>
              <NavLink 
                to="/3pl/management" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <Briefcase size={16} /> Management
                </div>
              </NavLink>
            </div>
          )}

          {/* Freight Menu */}
          <div 
            className="nav-item" 
            onClick={() => toggleMenu('freight')}
            style={{ marginBottom: expandedMenu === 'freight' ? 4 : 8 }}
          >
            <div className="nav-item-left">
              <Truck size={18} /> Freight Management
            </div>
            {expandedMenu === 'freight' ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>

          {expandedMenu === 'freight' && (
            <div style={{ paddingLeft: 12, marginBottom: 12 }}>
              <NavLink 
                to="/freight/operations" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <LayoutDashboard size={16} /> Operations
                </div>
              </NavLink>
              <NavLink 
                to="/freight/finance" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <Activity size={16} /> Finance
                </div>
              </NavLink>
              <NavLink 
                to="/freight/management" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <Briefcase size={16} /> Management
                </div>
              </NavLink>
              <NavLink 
                to="/freight/transportation" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <Truck size={16} /> Transportation
                </div>
              </NavLink>
            </div>
          )}
          
          {/* Fleet Menu */}
          <div 
            className="nav-item" 
            onClick={() => toggleMenu('fleet')}
            style={{ marginBottom: expandedMenu === 'fleet' ? 4 : 8 }}
          >
            <div className="nav-item-left">
              <Car size={18} /> Fleet Management
            </div>
            {expandedMenu === 'fleet' ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>

          {expandedMenu === 'fleet' && (
            <div style={{ paddingLeft: 12, marginBottom: 12 }}>
              <NavLink 
                to="/fleet/operations" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <LayoutDashboard size={16} /> Operations
                </div>
              </NavLink>
              <NavLink 
                to="/fleet/management" 
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={{ fontSize: 13, padding: '8px 12px' }}
              >
                <div className="nav-item-left">
                  <Briefcase size={16} /> Management & Costs
                </div>
              </NavLink>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}
