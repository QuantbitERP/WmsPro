import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import Login from '../Login';

// 3PL Pages
import WmsOperations from '../pages/3PL/OperationsDashboard';
import WmsManagement from '../pages/3PL/ManagementDashboard';

// Freight Pages
import FreightOperations from '../pages/Freight/Operations';
import FreightFinance from '../pages/Freight/Finance';
import FreightManagement from '../pages/Freight/Management';
import FreightTransportation from '../pages/Freight/Transportation';

// Fleet Pages
import FleetOperations from '../pages/Fleet/Operations';
import FleetManagement from '../pages/Fleet/Management';

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={<DashboardLayout />}>
        {/* Redirect root to /3pl/operations by default */}
        <Route index element={<Navigate to="/3pl/operations" replace />} />
        
        {/* 3PL Routes */}
        <Route path="3pl">
          <Route path="operations" element={<WmsOperations />} />
          <Route path="management" element={<WmsManagement />} />
        </Route>
        
        {/* Freight Routes */}
        <Route path="freight">
          <Route path="operations" element={<FreightOperations />} />
          <Route path="finance" element={<FreightFinance />} />
          <Route path="management" element={<FreightManagement />} />
          <Route path="transportation" element={<FreightTransportation />} />
        </Route>

        {/* Fleet Routes */}
        <Route path="fleet">
          <Route path="operations" element={<FleetOperations />} />
          <Route path="management" element={<FleetManagement />} />
        </Route>
      </Route>
    </Routes>
  );
}
