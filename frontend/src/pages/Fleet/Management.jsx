import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';
import { 
  DollarSign, TrendingUp, Key, ShieldAlert, Settings, Wrench, 
  BarChart2, Calendar, Loader, FileText, CheckCircle
} from 'lucide-react';

export default function FleetManagement() {
  const [vehicles, setVehicles] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [fuelEntries, setFuelEntries] = useState([]);
  const [rentals, setRentals] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const resVehicles = await axios.get('/api/resource/Vehicle Master?fields=["name","registration_number","make_and_model","current_odometer_reading_km"]&limit=100');
      const resExpenses = await axios.get('/api/resource/Vehicle Expense?fields=["name","vehicle","expense_date","amount","account","odometer_reading"]&order_by=creation desc&limit=100');
      const resFuel = await axios.get('/api/resource/Fuel Entry?fields=["name","vehicle","quantity_liters","rate_per_liter","posting_date"]&order_by=creation desc&limit=100');
      const resRentals = await axios.get('/api/resource/Rental Contract?fields=["name","customer","vehicle","contract_start_date","contract_end_date","rate_amount","docstatus"]&order_by=creation desc&limit=50');

      setVehicles(resVehicles.data.data || []);
      setExpenses(resExpenses.data.data || []);
      setFuelEntries(resFuel.data.data || []);
      setRentals(resRentals.data.data || []);
    } catch (err) {
      console.error("Error fetching fleet management data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Compute stats
  const totalExpenseAmt = expenses.reduce((sum, exp) => sum + (exp.amount || 0), 0);
  const totalFuelAmt = fuelEntries.reduce((sum, f) => sum + ((f.quantity_liters || 0) * (f.rate_per_liter || 1.10)), 0);
  const totalOperatingCosts = totalExpenseAmt + totalFuelAmt;
  const activeRentalsCount = rentals.filter(r => r.docstatus === 1).length;
  const totalRentalRevenue = rentals.filter(r => r.docstatus === 1).reduce((sum, r) => sum + (r.rate_amount || 0), 0);

  // Re-build Chart on data update
  useEffect(() => {
    if (loading || vehicles.length === 0) return;

    // Aggregate costs per vehicle
    const vehicleCosts = {};
    expenses.forEach(exp => {
      const v = exp.vehicle;
      vehicleCosts[v] = (vehicleCosts[v] || 0) + (exp.amount || 0);
    });
    fuelEntries.forEach(f => {
      const v = f.vehicle;
      vehicleCosts[v] = (vehicleCosts[v] || 0) + ((f.quantity_liters || 0) * (f.rate_per_liter || 1.10));
    });

    // Take top 5 vehicles by cost or all of them
    const labels = Object.keys(vehicleCosts).slice(0, 5);
    const data = labels.map(lbl => vehicleCosts[lbl]);

    const ctx = document.getElementById('expenseChart');
    if (!ctx) return;
    
    const existingChart = Chart.getChart('expenseChart');
    if (existingChart) existingChart.destroy();

    new Chart('expenseChart', {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total Expenses (OMR)',
          data: data,
          backgroundColor: '#3B82F6',
          borderColor: '#1D4ED8',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: '#E2E8F0' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }, [expenses, fuelEntries, vehicles, loading]);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '80vh', gap: '16px' }}>
        <Loader className="animate-spin" size={40} color="#2563EB" />
        <span style={{ fontSize: '15px', color: '#5A6A80', fontWeight: 500 }}>Loading Fleet Management & Cost Center...</span>
      </div>
    );
  }

  return (
    <div className="main-layout">
      <div className="content">
        {/* Page Header */}
        <div className="page-header">
          <div>
            <h1>Fleet Management & Financial Analysis</h1>
            <p>Track complete fleet overhead costs, operating expenses, and rental contract revenue streams</p>
          </div>
          <div className="header-right">
            <span className="period-pill" style={{ background: '#EFF6FF', color: '#1E40AF', border: '1px solid #BFDBFE' }}>Financial View</span>
          </div>
        </div>

        {/* Cost KPI Counters */}
        <div className="section-label">Fleet Cost Controls</div>
        <div className="grid-5" style={{ marginBottom: '24px' }}>
          <div className="kpi danger">
            <div className="kpi-label">Total Operating Cost</div>
            <div className="kpi-value" style={{ color: 'var(--red)' }}>OMR {totalOperatingCosts.toFixed(2)}</div>
            <div className="kpi-sub">Fuel + Maintenance</div>
            <div className="kpi-icon"><DollarSign size={20} color="#DC2626" /></div>
          </div>
          <div className="kpi info">
            <div className="kpi-label">Fuel Expenses</div>
            <div className="kpi-value">OMR {totalFuelAmt.toFixed(2)}</div>
            <div className="kpi-sub">Total Refuels Logged</div>
            <div className="kpi-icon"><TrendingUp size={20} color="#1D4ED8" /></div>
          </div>
          <div className="kpi success">
            <div className="kpi-label">Other Fleet Expenses</div>
            <div className="kpi-value" style={{ color: 'var(--green)' }}>OMR {totalExpenseAmt.toFixed(2)}</div>
            <div className="kpi-sub">Repairs, Tolls, Misc</div>
            <div className="kpi-icon"><DollarSign size={20} color="#047857" /></div>
          </div>
          <div className="kpi info">
            <div className="kpi-label">Active Rentals</div>
            <div className="kpi-value">{activeRentalsCount}</div>
            <div className="kpi-sub">Total rental streams</div>
            <div className="kpi-icon"><Key size={20} color="#1D4ED8" /></div>
          </div>
          <div className="kpi success">
            <div className="kpi-label">Rental Monthly Revenue</div>
            <div className="kpi-value" style={{ color: 'var(--green)' }}>OMR {totalRentalRevenue.toFixed(2)}</div>
            <div className="kpi-sub">Contractual Recurring Receipts</div>
            <div className="kpi-icon"><TrendingUp size={20} color="#047857" /></div>
          </div>
        </div>

        {/* Grid sections */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', marginBottom: '28px' }}>
          
          {/* Expenses Log Table */}
          <div className="glass-card" style={{ padding: '20px', borderRadius: '10px', background: '#fff', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} color="#2563EB" /> Recent Expense Logs
            </h3>
            {expenses.length > 0 ? (
              <table className="data-table" style={{ fontSize: '12px' }}>
                <thead>
                  <tr>
                    <th>Log ID</th>
                    <th>Vehicle</th>
                    <th>Date</th>
                    <th>GL Account</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {expenses.slice(0, 5).map(exp => (
                    <tr key={exp.name}>
                      <td className="mono link-cell">{exp.name}</td>
                      <td>{exp.vehicle}</td>
                      <td>{exp.expense_date}</td>
                      <td style={{ color: '#475569' }}>{exp.account?.split(' - ')[0]}</td>
                      <td className="mono" style={{ fontWeight: 600 }}>OMR {exp.amount?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px 0', color: '#94A3B8' }}>
                <FileText size={28} style={{ marginBottom: '8px' }} />
                <span>No expense records found</span>
              </div>
            )}
          </div>

          {/* Active Rental Contracts */}
          <div className="glass-card" style={{ padding: '20px', borderRadius: '10px', background: '#fff', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Key size={18} color="#10B981" /> Active Rental Contracts
            </h3>
            {rentals.length > 0 ? (
              <table className="data-table" style={{ fontSize: '12px' }}>
                <thead>
                  <tr>
                    <th>Contract ID</th>
                    <th>Customer</th>
                    <th>Vehicle</th>
                    <th>Monthly Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {rentals.map(contract => (
                    <tr key={contract.name}>
                      <td className="mono link-cell">{contract.name}</td>
                      <td>{contract.customer}</td>
                      <td>{contract.vehicle}</td>
                      <td className="mono" style={{ color: 'var(--green)', fontWeight: 600 }}>OMR {contract.rate_amount?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px 0', color: '#94A3B8' }}>
                <Key size={28} style={{ marginBottom: '8px' }} />
                <span>No active rental contracts</span>
              </div>
            )}
          </div>
        </div>

        {/* Cost By Vehicle Chart & Odometer Registry */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '28px' }}>
          {/* Chart */}
          <div className="glass-card" style={{ padding: '20px', borderRadius: '10px', background: '#fff', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={18} color="#2563EB" /> Expense Analysis by Vehicle
            </h3>
            <div style={{ position: 'relative', height: '220px' }}>
              <canvas id="expenseChart" height="220"></canvas>
            </div>
          </div>

          {/* Odometer & Maintenance Alerts */}
          <div className="glass-card" style={{ padding: '20px', borderRadius: '10px', background: '#fff', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Wrench size={18} color="#D97706" /> Maintenance & Odometer Tracking
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {vehicles.map(v => {
                const needsMaintenance = v.current_odometer_reading_km > 12100;
                return (
                  <div key={v.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'between', padding: '10px', borderRadius: '6px', border: '1px solid #F1F5F9', background: '#F8FAFC' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Wrench size={16} color={needsMaintenance ? "#EF4444" : "#10B981"} />
                      <div>
                        <div style={{ fontWeight: 600, color: '#1E293B', fontSize: '13px' }}>{v.make_and_model} ({v.registration_number})</div>
                        <div style={{ fontSize: '11px', color: '#64748B' }}>Odometer: {v.current_odometer_reading_km} km</div>
                      </div>
                    </div>
                    <div style={{ marginLeft: 'auto' }}>
                      {needsMaintenance ? (
                        <span style={{ fontSize: '10px', fontWeight: 600, padding: '3px 8px', borderRadius: '12px', background: '#FEE2E2', color: '#991B1B', border: '1px solid #FCA5A5' }}>
                          ⚠️ Maintenance Expired
                        </span>
                      ) : (
                        <span style={{ fontSize: '10px', fontWeight: 600, padding: '3px 8px', borderRadius: '12px', background: '#D1FAE5', color: '#065F46', border: '1px solid #6EE7B7' }}>
                          ✓ Healthy
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Financial Sidebar */}
      <div className="sidebar" style={{ borderLeft: '1px solid #E2E8F0', padding: '20px', background: '#F8FAFC' }}>
        <div className="sidebar-card" style={{ marginBottom: '20px' }}>
          <div className="sidebar-title">Audit Log alerts</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div className="alert-item critical" style={{ borderLeftColor: '#EF4444', background: '#FEF2F2' }}>
              <span className="alert-icon">🚨</span>
              <div>
                <div style={{ fontWeight: 600, color: '#1E293B' }}>Maintenance Overdue</div>
                <div className="alert-ref">Vehicle: MH-12-TX-EVE2</div>
                <div className="alert-time">Odometer exceeds plan limit</div>
              </div>
            </div>
            <div className="alert-item warning" style={{ borderLeftColor: '#10B981', background: '#EFF6FF' }}>
              <span className="alert-icon">✓</span>
              <div>
                <div style={{ fontWeight: 600, color: '#1E293B' }}>Recurring Bills Released</div>
                <div className="alert-ref">Rental Subscription plan active</div>
                <div className="alert-time">Next cycle: Sep 20th</div>
              </div>
            </div>
          </div>
        </div>

        <div className="sidebar-card">
          <div className="sidebar-title">Cost Distribution</div>
          <div style={{ fontSize: '13px', color: '#475569', lineHeight: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #E2E8F0' }}>
              <span>Fuel Entries</span>
              <span className="mono" style={{ fontWeight: 600 }}>OMR {totalFuelAmt.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #E2E8F0' }}>
              <span>Vehicle Maintenance</span>
              <span className="mono" style={{ fontWeight: 600 }}>OMR {totalExpenseAmt.toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontWeight: 'bold', paddingTop: '10px' }}>
              <span>Total overhead</span>
              <span className="mono">OMR {totalOperatingCosts.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
