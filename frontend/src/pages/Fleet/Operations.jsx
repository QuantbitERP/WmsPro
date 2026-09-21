import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';
import { 
  Car, User, Calendar, MapPin, Fuel, Send, 
  CheckCircle, AlertCircle, Plus, Eye, Loader, Clipboard
} from 'lucide-react';

export default function FleetOperations() {
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [tripRequests, setTripRequests] = useState([]);
  const [tripPlannings, setTripPlannings] = useState([]);
  const [tripLogs, setTripLogs] = useState([]);
  const [fuelEntries, setFuelEntries] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Form State for Quick Trip Request
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [newRequest, setNewRequest] = useState({
    expected_trip_start_date: '',
    expected_trip_end_date: '',
    purpose: '',
    requested_by: '',
    department: '',
    company: 'Quantbit Technologies Pvt Ltd' // default
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch Masters
      const resVehicles = await axios.get('/api/resource/Vehicle Master?fields=["name","registration_number","vehicle_type","status","current_odometer_reading_km"]&limit=100');
      const resDrivers = await axios.get('/api/resource/Driver Master?fields=["name","full_name","license_number","contact_number"]&limit=100');
      
      // Fetch Transactions
      const resReqs = await axios.get('/api/resource/Trip Request?fields=["name","posting_date","expected_trip_start_date","expected_trip_end_date","purpose","requested_by","trip_request_status"]&order_by=creation desc&limit=50');
      const resPlans = await axios.get('/api/resource/Trip Planning?fields=["name","posting_date","vehicle","driver","plan_start_date","plan_end_date","plan_status"]&order_by=creation desc&limit=50');
      const resLogs = await axios.get('/api/resource/Trip Log?fields=["name","posting_date","vehicle","driver","start_location","end_location","trip_status","starting_odometer","ending_odometer"]&order_by=creation desc&limit=50');
      const resFuel = await axios.get('/api/resource/Fuel Entry?fields=["name","posting_date","vehicle","driver","quantity_liters","rate_per_liter"]&order_by=creation desc&limit=10');

      setVehicles(resVehicles.data.data || []);
      setDrivers(resDrivers.data.data || []);
      setTripRequests(resReqs.data.data || []);
      setTripPlannings(resPlans.data.data || []);
      setTripLogs(resLogs.data.data || []);
      setFuelEntries(resFuel.data.data || []);

      // Fetch lookup helpers
      const resEmp = await axios.get('/api/resource/Employee?fields=["name","employee_name"]&limit=50');
      const resDept = await axios.get('/api/resource/Department?fields=["name","department_name"]&limit=50');
      setEmployees(resEmp.data.data || []);
      setDepartments(resDept.data.data || []);

    } catch (err) {
      console.error("Error fetching Fleet data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Re-build Chart on data update
  useEffect(() => {
    if (loading || vehicles.length === 0) return;

    // Count Vehicle types
    const types = {};
    vehicles.forEach(v => {
      types[v.vehicle_type] = (types[v.vehicle_type] || 0) + 1;
    });

    const ctx = document.getElementById('vehicleTypeChart');
    if (!ctx) return;
    
    const existingChart = Chart.getChart('vehicleTypeChart');
    if (existingChart) existingChart.destroy();

    new Chart('vehicleTypeChart', {
      type: 'doughnut',
      data: {
        labels: Object.keys(types),
        datasets: [{
          data: Object.values(types),
          backgroundColor: ['#1A56DB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#94A3B8'],
          borderWidth: 1,
          borderColor: '#fff'
        }]
      },
      options: {
        cutout: '70%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 8,
              padding: 10,
              font: { size: 10 }
            }
          }
        }
      }
    });
  }, [vehicles, loading]);

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    if (!newRequest.requested_by || !newRequest.purpose || !newRequest.expected_trip_start_date || !newRequest.expected_trip_end_date) {
      alert("Please fill in all mandatory fields.");
      return;
    }

    try {
      setSubmitting(true);
      // Format Datetime values to match DB format (YYYY-MM-DD HH:MM:SS)
      const start = newRequest.expected_trip_start_date.replace('T', ' ') + ':00';
      const end = newRequest.expected_trip_end_date.replace('T', ' ') + ':00';

      const payload = {
        doctype: 'Trip Request',
        posting_date: new Date().toISOString().split('T')[0],
        expected_trip_start_date: start,
        expected_trip_end_date: end,
        purpose: newRequest.purpose,
        requested_by: newRequest.requested_by,
        department: newRequest.department || undefined,
        company: newRequest.company,
        trip_request_status: 'Requested'
      };

      await axios.post('/api/resource/Trip Request', payload);
      
      // Reset request form
      setNewRequest({
        expected_trip_start_date: '',
        expected_trip_end_date: '',
        purpose: '',
        requested_by: '',
        department: '',
        company: 'Quantbit Technologies Pvt Ltd'
      });

      alert("Trip Request created successfully!");
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Error creating Trip Request: " + (err.response?.data?.message || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    let cls = 'badge blue';
    if (['Active', 'Planned', 'Assigned', 'Ongoing'].includes(status)) cls = 'badge blue';
    else if (['Completed', 'Released', 'Complete'].includes(status)) cls = 'badge green';
    else if (['Requested'].includes(status)) cls = 'badge amber';
    else if (['Cancelled', 'Incomplete', 'Inactive'].includes(status)) cls = 'badge red';
    return <span className={cls}>{status}</span>;
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '80vh', gap: '16px' }}>
        <Loader className="animate-spin" size={40} color="#2563EB" />
        <span style={{ fontSize: '15px', color: '#5A6A80', fontWeight: 500 }}>Loading Fleet Operations...</span>
      </div>
    );
  }

  return (
    <div className="main-layout">
      <div className="content">
        {/* Page Header */}
        <div className="page-header">
          <div>
            <h1>Fleet Operations Center</h1>
            <p>Monitor trips pipeline, handle dispatch requests and track fuel logs</p>
          </div>
          <div className="header-right">
            <button onClick={fetchData} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: '6px' }}>
              Refresh Data
            </button>
          </div>
        </div>

        {/* Live Counters */}
        <div className="section-label">Live Fleet Counters</div>
        <div className="grid-5" style={{ marginBottom: '24px' }}>
          <div className="kpi info">
            <div className="kpi-label">Active Vehicles</div>
            <div className="kpi-value">{vehicles.filter(v => v.status === 'Active').length}</div>
            <div className="kpi-sub">Total {vehicles.length} registered</div>
            <div className="kpi-icon"><Car size={20} color="#1D4ED8" /></div>
          </div>
          <div className="kpi success">
            <div className="kpi-label">Registered Drivers</div>
            <div className="kpi-value" style={{ color: 'var(--green)' }}>{drivers.length}</div>
            <div className="kpi-sub">Ready for Dispatch</div>
            <div className="kpi-icon"><User size={20} color="#047857" /></div>
          </div>
          <div className="kpi warning">
            <div className="kpi-label">Pending Requests</div>
            <div className="kpi-value" style={{ color: 'var(--amber)' }}>
              {tripRequests.filter(r => r.trip_request_status === 'Requested').length}
            </div>
            <div className="kpi-sub">Awaiting Assignment</div>
            <div className="kpi-icon"><Clipboard size={20} color="#B45309" /></div>
          </div>
          <div className="kpi info">
            <div className="kpi-label">Planned Journeys</div>
            <div className="kpi-value">{tripPlannings.filter(p => p.plan_status === 'Planned').length}</div>
            <div className="kpi-sub">Active schedules</div>
            <div className="kpi-icon"><Calendar size={20} color="#1D4ED8" /></div>
          </div>
          <div className="kpi success">
            <div className="kpi-label">Trips Logged</div>
            <div className="kpi-value" style={{ color: 'var(--green)' }}>{tripLogs.length}</div>
            <div className="kpi-sub">Historical executions</div>
            <div className="kpi-icon"><CheckCircle size={20} color="#047857" /></div>
          </div>
        </div>

        {/* Trip Planning & dispatch pipeline */}
        <div className="section-label">Fleet Dispatch Pipeline</div>
        <div className="pipeline-strip" style={{ marginBottom: '28px' }}>
          {/* Column 1: Requested */}
          <div className="pipeline-col">
            <div className="pipeline-col-head">Requested <span className="p-count amber">{tripRequests.filter(r => r.trip_request_status === 'Requested').length}</span></div>
            {tripRequests.filter(r => r.trip_request_status === 'Requested').map(req => (
              <div className="job-card" key={req.name}>
                <div className="seg-pill air">REQUEST</div>
                <div className="job-card-no">{req.name}</div>
                <div className="job-card-cust">Emp: {req.requested_by}</div>
                <div className="job-card-meta">{req.purpose}</div>
                <div className="job-card-days warn">Start: {req.expected_trip_start_date?.split(' ')[0]}</div>
              </div>
            ))}
            {tripRequests.filter(r => r.trip_request_status === 'Requested').length === 0 && (
              <div style={{ textAlign: 'center', padding: '16px', color: '#94A3B8', fontSize: '12px' }}>No pending requests</div>
            )}
          </div>

          {/* Column 2: Planned */}
          <div className="pipeline-col">
            <div className="pipeline-col-head">Planned <span className="p-count blue">{tripPlannings.filter(p => p.plan_status === 'Planned').length}</span></div>
            {tripPlannings.filter(p => p.plan_status === 'Planned').map(plan => (
              <div className="job-card" key={plan.name}>
                <div className="seg-pill">PLANNED</div>
                <div className="job-card-no">{plan.name}</div>
                <div className="job-card-cust">Vehicle: {plan.vehicle}</div>
                <div className="job-card-meta">Driver: {plan.driver}</div>
                <div className="job-card-days ok">ETA: {plan.plan_start_date?.split(' ')[0]}</div>
              </div>
            ))}
            {tripPlannings.filter(p => p.plan_status === 'Planned').length === 0 && (
              <div style={{ textAlign: 'center', padding: '16px', color: '#94A3B8', fontSize: '12px' }}>No active plans</div>
            )}
          </div>

          {/* Column 3: Logged / Done */}
          <div className="pipeline-col">
            <div className="pipeline-col-head">Logged Trips <span className="p-count green">{tripLogs.length}</span></div>
            {tripLogs.slice(0, 3).map(log => (
              <div className="job-card" key={log.name}>
                <div className="seg-pill land">LOGGED</div>
                <div className="job-card-no">{log.name}</div>
                <div className="job-card-cust">{log.vehicle} ({log.driver})</div>
                <div className="job-card-meta">{log.start_location} → {log.end_location}</div>
                <div className="job-card-days ok">Odo: {log.starting_odometer} - {log.ending_odometer}</div>
              </div>
            ))}
            {tripLogs.length === 0 && (
              <div style={{ textAlign: 'center', padding: '16px', color: '#94A3B8', fontSize: '12px' }}>No logged trips</div>
            )}
          </div>
        </div>

        {/* Dynamic Tables & Forms */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', marginBottom: '28px' }}>
          {/* Quick Request Form */}
          <div className="glass-card" style={{ padding: '20px', borderRadius: '10px', background: '#fff', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Plus size={18} color="#2563EB" /> Quick Trip Booking Request
            </h3>
            <form onSubmit={handleCreateRequest} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>Requested By (Employee) *</label>
                <select 
                  className="filter-select"
                  style={{ width: '100%', padding: '8px' }}
                  value={newRequest.requested_by}
                  onChange={e => setNewRequest({...newRequest, requested_by: e.target.value})}
                  required
                >
                  <option value="">Select Employee</option>
                  {employees.map(emp => (
                    <option key={emp.name} value={emp.name}>{emp.employee_name} ({emp.name})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>Department</label>
                <select 
                  className="filter-select"
                  style={{ width: '100%', padding: '8px' }}
                  value={newRequest.department}
                  onChange={e => setNewRequest({...newRequest, department: e.target.value})}
                >
                  <option value="">Select Department</option>
                  {departments.map(dept => (
                    <option key={dept.name} value={dept.name}>{dept.department_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>Start Time *</label>
                <input 
                  type="datetime-local" 
                  className="filter-select"
                  style={{ width: '100%', padding: '6px' }}
                  value={newRequest.expected_trip_start_date}
                  onChange={e => setNewRequest({...newRequest, expected_trip_start_date: e.target.value})}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>End Time *</label>
                <input 
                  type="datetime-local" 
                  className="filter-select"
                  style={{ width: '100%', padding: '6px' }}
                  value={newRequest.expected_trip_end_date}
                  onChange={e => setNewRequest({...newRequest, expected_trip_end_date: e.target.value})}
                  required
                />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '4px' }}>Trip Purpose *</label>
                <textarea 
                  className="filter-select"
                  rows="2"
                  style={{ width: '100%', padding: '8px', fontFamily: 'inherit' }}
                  placeholder="e.g. Visit site, transport parts, warehouse delivery..."
                  value={newRequest.purpose}
                  onChange={e => setNewRequest({...newRequest, purpose: e.target.value})}
                  required
                />
              </div>

              <div style={{ gridColumn: 'span 2', textAlign: 'right', marginTop: '4px' }}>
                <button type="submit" className="btn-primary" disabled={submitting} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '6px' }}>
                  {submitting ? <Loader className="animate-spin" size={14} /> : <Send size={14} />}
                  Submit Booking Request
                </button>
              </div>
            </form>
          </div>

          {/* Refuel Logs Queue */}
          <div className="glass-card" style={{ padding: '20px', borderRadius: '10px', background: '#fff', border: '1px solid #E2E8F0' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Fuel size={18} color="#D97706" /> Recent Refueling Entries
            </h3>
            {fuelEntries.length > 0 ? (
              <table className="data-table" style={{ fontSize: '12px' }}>
                <thead>
                  <tr>
                    <th>Entry ID</th>
                    <th>Vehicle</th>
                    <th>Driver</th>
                    <th>Quantity (L)</th>
                    <th>Cost (OMR)</th>
                  </tr>
                </thead>
                <tbody>
                  {fuelEntries.slice(0, 5).map(fe => (
                    <tr key={fe.name}>
                      <td className="mono link-cell">{fe.name}</td>
                      <td>{fe.vehicle}</td>
                      <td>{fe.driver}</td>
                      <td>{fe.quantity_liters} L</td>
                      <td className="mono">OMR {(fe.quantity_liters * (fe.rate_per_liter || 1.10)).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px 0', color: '#94A3B8' }}>
                <Fuel size={28} style={{ marginBottom: '8px' }} />
                <span>No refueling records found</span>
              </div>
            )}
          </div>
        </div>

        {/* Vehicle Registry Details */}
        <div className="section-label">Vehicle Registry Status</div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Reg Number</th>
              <th>Vehicle Name/Type</th>
              <th>Odometer Reading</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map(v => (
              <tr key={v.name}>
                <td className="mono link-cell">{v.registration_number}</td>
                <td>{v.name} ({v.vehicle_type})</td>
                <td className="mono">{v.current_odometer_reading_km} km</td>
                <td>{getStatusBadge(v.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Operations Sidebar */}
      <div className="sidebar" style={{ borderLeft: '1px solid #E2E8F0', padding: '20px', background: '#F8FAFC' }}>
        <div className="sidebar-card" style={{ marginBottom: '20px' }}>
          <div className="sidebar-title">Active Drivers</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {drivers.slice(0, 6).map(dr => (
              <div key={dr.name} className="alert-item warning" style={{ borderLeftColor: '#3B82F6', background: '#EFF6FF' }}>
                <span className="alert-icon">👤</span>
                <div>
                  <div style={{ fontWeight: 600, color: '#1E293B' }}>{dr.full_name}</div>
                  <div className="alert-ref">Lic: {dr.license_number}</div>
                  <div className="alert-time">Mob: {dr.contact_number}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="sidebar-card">
          <div className="sidebar-title">Vehicle Mix Chart</div>
          <div style={{ position: 'relative', height: '220px' }}>
            <canvas id="vehicleTypeChart" height="220"></canvas>
          </div>
        </div>
      </div>
    </div>
  );
}
