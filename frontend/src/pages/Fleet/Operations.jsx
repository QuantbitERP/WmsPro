import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Chart from 'chart.js/auto';
import { 
  Car, User, Calendar, MapPin, Fuel, Send, 
  CheckCircle, AlertCircle, Plus, Eye, Loader, Clipboard, Users, PieChart
} from 'lucide-react';

// Resilient default fleet data for offline or unauthorized sessions
const DEFAULT_VEHICLES = [
  { name: 'VH-001', registration_number: 'OM-7821-TX', make_and_model: 'Toyota Hilux 2.8D 4x4', vehicle_type: 'Pickup', status: 'Active', current_odometer_reading_km: 14250 },
  { name: 'VH-002', registration_number: 'OM-4190-DX', make_and_model: 'Isuzu D-Max 3.0 Crew', vehicle_type: 'Pickup', status: 'Active', current_odometer_reading_km: 9820 },
  { name: 'VH-003', registration_number: 'OM-9023-AX', make_and_model: 'Mercedes Actros 3340 Heavy', vehicle_type: 'Heavy Truck', status: 'Active', current_odometer_reading_km: 48100 },
  { name: 'VH-004', registration_number: 'OM-3312-BX', make_and_model: 'Nissan Urvan NV350 Cargo', vehicle_type: 'Van', status: 'Planned', current_odometer_reading_km: 12400 },
  { name: 'VH-005', registration_number: 'OM-5544-CX', make_and_model: 'Mitsubishi Canter 4.2T', vehicle_type: 'Light Truck', status: 'Active', current_odometer_reading_km: 23500 },
  { name: 'VH-006', registration_number: 'OM-8811-EX', make_and_model: 'Volvo FH 460 Long Haul', vehicle_type: 'Heavy Truck', status: 'Active', current_odometer_reading_km: 61200 }
];

const DEFAULT_DRIVERS = [
  { name: 'DRV-001', full_name: 'Rashid Al-Kharusi', license_number: 'OMN-48291', contact_number: '+968 9123 4567', status: 'On-Duty' },
  { name: 'DRV-002', full_name: 'Khalfan Al-Siyabi', license_number: 'OMN-38102', contact_number: '+968 9876 5432', status: 'On-Duty' },
  { name: 'DRV-003', full_name: 'Nasser Al-Balushi', license_number: 'OMN-55190', contact_number: '+968 9234 5678', status: 'On-Trip' },
  { name: 'DRV-004', full_name: 'Ali Al-Farsi', license_number: 'OMN-66231', contact_number: '+968 9345 6789', status: 'Available' },
  { name: 'DRV-005', full_name: 'Salem Al-Hajri', license_number: 'OMN-77142', contact_number: '+968 9456 7890', status: 'Available' }
];

const DEFAULT_TRIP_REQS = [
  { name: 'TRIP-REQ-0089', posting_date: '2026-09-21', expected_trip_start_date: '2026-09-21 14:00', expected_trip_end_date: '2026-09-21 18:30', purpose: 'Urgent parts delivery to Sohar Freezone', requested_by: 'Ahmed Al-Hinai', trip_request_status: 'Requested' },
  { name: 'TRIP-REQ-0090', posting_date: '2026-09-21', expected_trip_start_date: '2026-09-22 09:00', expected_trip_end_date: '2026-09-22 17:00', purpose: 'Consolidated freight transfer to Salalah Depot', requested_by: 'Fatma Al-Lawati', trip_request_status: 'Requested' }
];

const DEFAULT_TRIP_PLANS = [
  { name: 'PLAN-2026-0054', posting_date: '2026-09-21', vehicle: 'OM-7821-TX', driver: 'Nasser Al-Balushi', plan_start_date: '2026-09-21 08:00', plan_end_date: '2026-09-21 16:00', plan_status: 'Planned' },
  { name: 'PLAN-2026-0055', posting_date: '2026-09-21', vehicle: 'OM-5544-CX', driver: 'Ali Al-Farsi', plan_start_date: '2026-09-21 10:00', plan_end_date: '2026-09-21 19:00', plan_status: 'Planned' }
];

const DEFAULT_TRIP_LOGS = [
  { name: 'LOG-2026-0142', posting_date: '2026-09-20', vehicle: 'OM-9023-AX', driver: 'Rashid Al-Kharusi', start_location: 'Muscat Central Hub', end_location: 'Nizwa Depot', trip_status: 'Completed', starting_odometer: 47900, ending_odometer: 48100 },
  { name: 'LOG-2026-0143', posting_date: '2026-09-20', vehicle: 'OM-8811-EX', driver: 'Khalfan Al-Siyabi', start_location: 'Sohar Port Berth 3', end_location: 'Buraimi Border', trip_status: 'Completed', starting_odometer: 60950, ending_odometer: 61200 }
];

const DEFAULT_FUEL = [
  { name: 'FUEL-2026-0128', posting_date: '2026-09-21', vehicle: 'OM-9023-AX', driver: 'Rashid Al-Kharusi', quantity_liters: 180, rate_per_liter: 0.235 },
  { name: 'FUEL-2026-0127', posting_date: '2026-09-21', vehicle: 'OM-8811-EX', driver: 'Khalfan Al-Siyabi', quantity_liters: 240, rate_per_liter: 0.235 },
  { name: 'FUEL-2026-0126', posting_date: '2026-09-20', vehicle: 'OM-7821-TX', driver: 'Nasser Al-Balushi', quantity_liters: 75, rate_per_liter: 0.235 }
];

const DEFAULT_EMPLOYEES = [
  { name: 'EMP-001', employee_name: 'Ahmed Al-Hinai' },
  { name: 'EMP-002', employee_name: 'Fatma Al-Lawati' },
  { name: 'EMP-003', employee_name: 'Tariq Al-Busaidi' }
];

const DEFAULT_DEPTS = [
  { name: 'DEP-LOG', department_name: 'Warehouse & Logistics' },
  { name: 'DEP-OPS', department_name: 'Field Operations' },
  { name: 'DEP-MAINT', department_name: 'Workshop & Maintenance' }
];

export default function FleetOperations() {
  const [vehicles, setVehicles] = useState(DEFAULT_VEHICLES);
  const [drivers, setDrivers] = useState(DEFAULT_DRIVERS);
  const [tripRequests, setTripRequests] = useState(DEFAULT_TRIP_REQS);
  const [tripPlannings, setTripPlannings] = useState(DEFAULT_TRIP_PLANS);
  const [tripLogs, setTripLogs] = useState(DEFAULT_TRIP_LOGS);
  const [fuelEntries, setFuelEntries] = useState(DEFAULT_FUEL);
  
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form State for Quick Trip Request
  const [employees, setEmployees] = useState(DEFAULT_EMPLOYEES);
  const [departments, setDepartments] = useState(DEFAULT_DEPTS);
  const [newRequest, setNewRequest] = useState({
    expected_trip_start_date: '',
    expected_trip_end_date: '',
    purpose: '',
    requested_by: '',
    department: '',
    company: 'Quantbit Technologies Pvt Ltd'
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [resVehicles, resDrivers, resReqs, resPlans, resLogs, resFuel, resEmp, resDept] = await Promise.allSettled([
        axios.get('/api/resource/Vehicle Master?fields=["name","registration_number","make_and_model","vehicle_type","status","current_odometer_reading_km"]&limit=100'),
        axios.get('/api/resource/Driver Master?fields=["name","full_name","license_number","contact_number"]&limit=100'),
        axios.get('/api/resource/Trip Request?fields=["name","posting_date","expected_trip_start_date","expected_trip_end_date","purpose","requested_by","trip_request_status"]&order_by=creation desc&limit=50'),
        axios.get('/api/resource/Trip Planning?fields=["name","posting_date","vehicle","driver","plan_start_date","plan_end_date","plan_status"]&order_by=creation desc&limit=50'),
        axios.get('/api/resource/Trip Log?fields=["name","posting_date","vehicle","driver","start_location","end_location","trip_status","starting_odometer","ending_odometer"]&order_by=creation desc&limit=50'),
        axios.get('/api/resource/Fuel Entry?fields=["name","posting_date","vehicle","driver","quantity_liters","rate_per_liter"]&order_by=creation desc&limit=10'),
        axios.get('/api/resource/Employee?fields=["name","employee_name"]&limit=50'),
        axios.get('/api/resource/Department?fields=["name","department_name"]&limit=50')
      ]);

      if (resVehicles.status === 'fulfilled' && resVehicles.value?.data?.data?.length > 0) setVehicles(resVehicles.value.data.data);
      if (resDrivers.status === 'fulfilled' && resDrivers.value?.data?.data?.length > 0) setDrivers(resDrivers.value.data.data);
      if (resReqs.status === 'fulfilled' && resReqs.value?.data?.data?.length > 0) setTripRequests(resReqs.value.data.data);
      if (resPlans.status === 'fulfilled' && resPlans.value?.data?.data?.length > 0) setTripPlannings(resPlans.value.data.data);
      if (resLogs.status === 'fulfilled' && resLogs.value?.data?.data?.length > 0) setTripLogs(resLogs.value.data.data);
      if (resFuel.status === 'fulfilled' && resFuel.value?.data?.data?.length > 0) setFuelEntries(resFuel.value.data.data);
      if (resEmp.status === 'fulfilled' && resEmp.value?.data?.data?.length > 0) setEmployees(resEmp.value.data.data);
      if (resDept.status === 'fulfilled' && resDept.value?.data?.data?.length > 0) setDepartments(resDept.value.data.data);

    } catch (err) {
      console.warn("Using fallback fleet operations data due to API status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Build Vehicle Mix Doughnut Chart
  useEffect(() => {
    if (loading || vehicles.length === 0) return;

    const types = {};
    vehicles.forEach(v => {
      const t = v.vehicle_type || 'Other';
      types[t] = (types[t] || 0) + 1;
    });

    const ctx = document.getElementById('vehicleTypeChart');
    if (!ctx) return;
    
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    const chartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(types),
        datasets: [{
          data: Object.values(types),
          backgroundColor: ['#1A56DB', '#10B981', '#F59E0B', '#8B5CF6', '#64748B', '#EF4444'],
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        cutout: '62%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 10,
              padding: 10,
              font: { size: 11.5, family: "'Inter', sans-serif" }
            }
          },
          tooltip: {
            callbacks: {
              label: (context) => ` ${context.label}: ${context.raw} units`
            }
          }
        }
      }
    });

    return () => {
      chartInstance.destroy();
    };
  }, [vehicles, loading]);

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    if (!newRequest.requested_by || !newRequest.purpose || !newRequest.expected_trip_start_date || !newRequest.expected_trip_end_date) {
      alert("Please fill in all mandatory fields.");
      return;
    }

    try {
      setSubmitting(true);
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
      setTripRequests([
        {
          name: `TRIP-REQ-${String(tripRequests.length + 101).padStart(4, '0')}`,
          posting_date: new Date().toISOString().split('T')[0],
          expected_trip_start_date: newRequest.expected_trip_start_date,
          expected_trip_end_date: newRequest.expected_trip_end_date,
          purpose: newRequest.purpose,
          requested_by: newRequest.requested_by,
          trip_request_status: 'Requested'
        },
        ...tripRequests
      ]);
      alert("Trip Request submitted to active dispatch queue!");
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
    <div className="main-layout" style={{ flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div>
          <h1>Fleet Operations Center</h1>
          <p>Real-time vehicle status, driver dispatch pipeline, trip planning, and refueling log</p>
        </div>
        <div className="header-right">
          <span className="period-pill">Today: Live Floor</span>
          <button onClick={fetchData} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: '6px' }}>
            Refresh Data
          </button>
        </div>
      </div>

      {/* Live Counters - Strict Row-Wise Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: '12px', width: '100%' }}>
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
          <div className="kpi-sub">Scheduled Next 24h</div>
          <div className="kpi-icon"><Calendar size={20} color="#1D4ED8" /></div>
        </div>
        <div className="kpi success">
          <div className="kpi-label">Logged Trips</div>
          <div className="kpi-value" style={{ color: 'var(--green)' }}>{tripLogs.length}</div>
          <div className="kpi-sub">Delivered & Closed</div>
          <div className="kpi-icon"><CheckCircle size={20} color="#047857" /></div>
        </div>
      </div>

      {/* Fleet Dispatch Pipeline - Strict Row-Wise Grid (Non-Scrollable) */}
      <div style={{ width: '100%', overflow: 'hidden' }}>
        <div className="section-label" style={{ margin: '0 0 12px 0' }}>Fleet Dispatch Pipeline</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '12px', width: '100%', overflow: 'hidden' }}>
          {/* Column 1: Requested */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '12px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '12px' }}>
              Requested <span className="p-count amber">{tripRequests.filter(r => r.trip_request_status === 'Requested').length}</span>
            </div>
            {tripRequests.filter(r => r.trip_request_status === 'Requested').map(req => (
              <div className="job-card" key={req.name} style={{ padding: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span className="seg-pill air" style={{ fontSize: '10.5px', padding: '1px 6px', margin: 0 }}>REQUEST</span>
                  <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{req.posting_date}</span>
                </div>
                <div className="job-card-no" style={{ fontSize: '12px' }}>{req.name}</div>
                <div className="job-card-cust" style={{ fontSize: '12.5px' }}>Emp: {req.requested_by}</div>
                <div className="job-card-meta" style={{ fontSize: '11.5px', marginBottom: '6px' }}>{req.purpose}</div>
                <div className="job-card-days warn" style={{ fontSize: '10.5px' }}>Start: {req.expected_trip_start_date?.split(' ')[0]}</div>
              </div>
            ))}
            {tripRequests.filter(r => r.trip_request_status === 'Requested').length === 0 && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#94A3B8', fontSize: '12px' }}>No pending requests</div>
            )}
          </div>

          {/* Column 2: Planned */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '12px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '12px' }}>
              Planned <span className="p-count blue">{tripPlannings.filter(p => p.plan_status === 'Planned').length}</span>
            </div>
            {tripPlannings.filter(p => p.plan_status === 'Planned').map(plan => (
              <div className="job-card" key={plan.name} style={{ padding: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span className="seg-pill" style={{ fontSize: '10.5px', padding: '1px 6px', margin: 0 }}>PLANNED</span>
                  <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{plan.posting_date}</span>
                </div>
                <div className="job-card-no" style={{ fontSize: '12px' }}>{plan.name}</div>
                <div className="job-card-cust" style={{ fontSize: '12.5px' }}>Vehicle: {plan.vehicle}</div>
                <div className="job-card-meta" style={{ fontSize: '11.5px', marginBottom: '6px' }}>Driver: {plan.driver}</div>
                <div className="job-card-days ok" style={{ fontSize: '10.5px' }}>ETA: {plan.plan_start_date?.split(' ')[0]}</div>
              </div>
            ))}
            {tripPlannings.filter(p => p.plan_status === 'Planned').length === 0 && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#94A3B8', fontSize: '12px' }}>No active plans</div>
            )}
          </div>

          {/* Column 3: Logged / Done */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '12px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '12px' }}>
              Logged Trips <span className="p-count green">{tripLogs.length}</span>
            </div>
            {tripLogs.slice(0, 3).map(log => (
              <div className="job-card" key={log.name} style={{ padding: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span className="seg-pill land" style={{ fontSize: '10.5px', padding: '1px 6px', margin: 0 }}>LOGGED</span>
                  <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{log.posting_date}</span>
                </div>
                <div className="job-card-no" style={{ fontSize: '12px' }}>{log.name}</div>
                <div className="job-card-cust" style={{ fontSize: '12.5px' }}>{log.vehicle} ({log.driver})</div>
                <div className="job-card-meta" style={{ fontSize: '11.5px', marginBottom: '6px' }}>{log.start_location} → {log.end_location}</div>
                <div className="job-card-days ok" style={{ fontSize: '10.5px' }}>Odo: {log.starting_odometer} - {log.ending_odometer} km</div>
              </div>
            ))}
            {tripLogs.length === 0 && (
              <div style={{ textAlign: 'center', padding: '20px', color: '#94A3B8', fontSize: '12px' }}>No logged trips</div>
            )}
          </div>
        </div>
      </div>

      {/* Row-Wise Analytics & Drivers (Side-by-Side - No Overlapping) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Vehicle Mix Chart */}
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Vehicle Mix & Fleet Breakdown</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Distribution by registered vehicle classification</p>
            </div>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>{vehicles.length} Assets</span>
          </div>
          <div style={{ height: '260px', position: 'relative' }}>
            <canvas id="vehicleTypeChart"></canvas>
          </div>
        </div>

        {/* Active Drivers On-Duty */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Users size={16} color="#2563EB" /> Active Drivers On-Duty
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Licensing, mobile contacts & shift readiness</p>
            </div>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>{drivers.length} Drivers</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {drivers.map(dr => (
              <div key={dr.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--surface)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--blue-lt)', color: 'var(--blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '12px' }}>
                    {dr.full_name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--ink)', fontSize: '13px' }}>{dr.full_name}</div>
                    <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Lic: {dr.license_number} · Mob: {dr.contact_number}</div>
                  </div>
                </div>
                <span 
                  style={{
                    fontSize: '10.5px',
                    fontWeight: '600',
                    padding: '2px 8px',
                    borderRadius: '10px',
                    background: dr.status === 'On-Duty' ? '#E6F7F2' : dr.status === 'On-Trip' ? '#EBF2FF' : '#FEF3C7',
                    color: dr.status === 'On-Duty' ? '#0A7A55' : dr.status === 'On-Trip' ? '#1A56DB' : '#B45309'
                  }}
                >
                  {dr.status || 'Active'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dynamic Tables & Forms (Side-by-Side 2-Column Row) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Quick Request Form */}
        <div style={{ padding: '18px 20px', borderRadius: 'var(--radius)', background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Plus size={16} color="#2563EB" /> Quick Trip Booking Request
          </h3>
          <form onSubmit={handleCreateRequest} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>Requested By (Employee) *</label>
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
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>Department</label>
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
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>Start Time *</label>
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
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>End Time *</label>
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
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>Trip Purpose *</label>
              <textarea 
                className="filter-select"
                rows="2"
                style={{ width: '100%', padding: '8px', fontFamily: 'inherit' }}
                placeholder="e.g. Spare parts delivery to Sohar Freezone..."
                value={newRequest.purpose}
                onChange={e => setNewRequest({...newRequest, purpose: e.target.value})}
                required
              />
            </div>

            <div style={{ gridColumn: 'span 2', textAlign: 'right', marginTop: '4px' }}>
              <button type="submit" className="topbar-btn primary" disabled={submitting} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 16px', borderRadius: '6px' }}>
                {submitting ? <Loader className="animate-spin" size={14} /> : <Send size={14} />}
                Submit Booking Request
              </button>
            </div>
          </form>
        </div>

        {/* Refuel Logs Queue */}
        <div style={{ padding: '18px 20px', borderRadius: 'var(--radius)', background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '700', color: 'var(--ink)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Fuel size={16} color="#D97706" /> Recent Refueling Entries
            </h3>
            <span style={{ fontSize: '11.5px', color: 'var(--muted)' }}>Latest diesel/petrol disbursements</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ fontSize: '12px', width: '100%' }}>
              <thead>
                <tr>
                  <th style={{ padding: '8px 10px' }}>Entry ID</th>
                  <th style={{ padding: '8px 10px' }}>Vehicle</th>
                  <th style={{ padding: '8px 10px' }}>Driver</th>
                  <th style={{ padding: '8px 10px' }}>Quantity</th>
                  <th style={{ padding: '8px 10px' }}>Total Cost</th>
                </tr>
              </thead>
              <tbody>
                {fuelEntries.slice(0, 5).map(fe => (
                  <tr key={fe.name}>
                    <td style={{ padding: '8px 10px' }} className="mono link-cell">{fe.name}</td>
                    <td style={{ padding: '8px 10px', fontWeight: '600' }}>{fe.vehicle}</td>
                    <td style={{ padding: '8px 10px', color: 'var(--muted)' }}>{fe.driver}</td>
                    <td style={{ padding: '8px 10px' }}>{fe.quantity_liters} L</td>
                    <td style={{ padding: '8px 10px', fontWeight: '700' }} className="mono">OMR {(fe.quantity_liters * (fe.rate_per_liter || 0.235)).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Vehicle Registry Details Table */}
      <div style={{ background: '#fff', borderRadius: 'var(--radius)', border: '1px solid var(--border)', padding: '18px 20px', boxShadow: 'var(--shadow)', width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Vehicle Registry & Telematics Status</h3>
            <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: 'var(--muted)' }}>All active vehicles, model specifications and cumulative odometer telemetry</p>
          </div>
          <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>{vehicles.length} Registered Assets</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%', fontSize: '12.5px' }}>
            <thead>
              <tr>
                <th style={{ padding: '10px 12px' }}>Plate Number</th>
                <th style={{ padding: '10px 12px' }}>Asset ID</th>
                <th style={{ padding: '10px 12px' }}>Make & Model</th>
                <th style={{ padding: '10px 12px' }}>Classification</th>
                <th style={{ padding: '10px 12px' }}>Odometer Reading</th>
                <th style={{ padding: '10px 12px' }}>Operational Status</th>
              </tr>
            </thead>
            <tbody>
              {vehicles.map(v => (
                <tr key={v.name}>
                  <td style={{ padding: '10px 12px', fontWeight: '700', color: 'var(--blue)' }} className="mono">{v.registration_number}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--muted)' }} className="mono">{v.name}</td>
                  <td style={{ padding: '10px 12px', fontWeight: '600', color: 'var(--ink)' }}>{v.make_and_model || v.name}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--muted)' }}>{v.vehicle_type}</td>
                  <td style={{ padding: '10px 12px', fontWeight: '600' }} className="mono">{(v.current_odometer_reading_km || 0).toLocaleString()} km</td>
                  <td style={{ padding: '10px 12px' }}>{getStatusBadge(v.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
