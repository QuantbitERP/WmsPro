import React, { useState, useEffect } from 'react';
import Chart from 'chart.js/auto';
import { 
  Wrench, Car, Clock, CheckCircle2, AlertTriangle, 
  User, Check, Eye, Plus, ArrowUpRight, ShieldAlert,
  Activity, RefreshCw, Filter, Layers, Gauge
} from 'lucide-react';

export default function WorkshopOperations() {
  const [selectedFilter, setSelectedFilter] = useState('All');
  const [selectedBayType, setSelectedBayType] = useState('All');

  // Static Workshop Data structured according to DocTypes
  const kpis = [
    { label: 'Active Job Cards', value: '18', sub: '↑ 4 since yesterday', trend: 'up', type: 'info', icon: '🔧' },
    { label: 'Bay Utilization', value: '83%', sub: '5 of 6 bays occupied', trend: 'up', type: 'warning', icon: '🏢' },
    { label: 'Pending Inspections', value: '7', sub: '3 Rental return, 2 Breakdown', trend: 'down', type: 'danger', icon: '🔍' },
    { label: 'Awaiting Spares', value: '4', sub: '2 POs dispatched', trend: 'neutral', type: 'warning', icon: '📦' },
    { label: 'Ready for Release', value: '6', sub: 'QC checklist cleared', trend: 'up', type: 'success', icon: '✅' },
  ];

  const bays = [
    {
      id: 'BAY-01',
      name: 'Bay 1 - Heavy Mechanical',
      type: 'General Repair',
      status: 'Occupied',
      hasLift: true,
      vehicle: 'VH-0104 (Volvo FH16)',
      jobCard: 'JC-2026-0042',
      technician: 'Rajesh Kumar (Sr. Tech)',
      issue: 'Engine overhaul & injector calibration',
      progress: 75,
      eta: 'Today, 16:30'
    },
    {
      id: 'BAY-02',
      name: 'Bay 2 - Body Shop & Prep',
      type: 'Body Shop',
      status: 'Occupied',
      hasLift: false,
      vehicle: 'VH-0089 (Tata Prima 4928)',
      jobCard: 'JC-2026-0039',
      technician: 'Suresh Patil (Body Specialist)',
      issue: 'Cabin denting & primer coating',
      progress: 45,
      eta: 'Tomorrow, 12:00'
    },
    {
      id: 'BAY-03',
      name: 'Bay 3 - Electrical & Diagnostics',
      type: 'Electrical',
      status: 'Occupied',
      hasLift: true,
      vehicle: 'VH-0211 (BharatBenz 2823)',
      jobCard: 'JC-2026-0045',
      technician: 'Amit Verma (Auto Electrician)',
      issue: 'CAN-bus wiring & alternator replacement',
      progress: 90,
      eta: 'Today, 14:00'
    },
    {
      id: 'BAY-04',
      name: 'Bay 4 - Express Lube & Service',
      type: 'General Repair',
      status: 'Available',
      hasLift: true,
      vehicle: 'None',
      jobCard: '-',
      technician: 'Ready for assignment',
      issue: 'Bay sanitized and ready for vehicle intake',
      progress: 0,
      eta: '-'
    },
    {
      id: 'BAY-05',
      name: 'Bay 5 - Tyres, Brakes & Alignment',
      type: 'Tyres',
      status: 'Occupied',
      hasLift: true,
      vehicle: 'VH-0340 (Eicher Pro 6035)',
      jobCard: 'JC-2026-0046',
      technician: 'Vikram Singh (Tyre & Brake Tech)',
      issue: 'Full axle brake pads + dual tyre renewal',
      progress: 60,
      eta: 'Today, 17:00'
    },
    {
      id: 'BAY-06',
      name: 'Bay 6 - Wash & Final Detailing',
      type: 'Wash Bay',
      status: 'Occupied',
      hasLift: false,
      vehicle: 'VH-0199 (Ashok Leyland 4220)',
      jobCard: 'JC-2026-0038',
      technician: 'Ganesh Shinde (Detailer)',
      issue: 'Pre-handover pressure wash & degreasing',
      progress: 85,
      eta: 'Today, 13:30'
    }
  ];

  const pipeline = {
    intake: [
      { id: 'WI-2026-0081', vehicle: 'VH-0288 (Tata Signa)', type: 'Rental Return', date: 'Today, 09:15', status: 'Draft', inspector: 'S. Nambiar', critical: false },
      { id: 'WI-2026-0082', vehicle: 'VH-0145 (BharatBenz 3528)', type: 'Breakdown', date: 'Today, 10:30', status: 'Inspected', inspector: 'A. Verma', critical: true },
      { id: 'WI-2026-0083', vehicle: 'VH-0301 (Mahindra Blazo)', type: 'Scheduled Service', date: 'Today, 11:00', status: 'Inspected', inspector: 'R. Kumar', critical: false }
    ],
    pendingApproval: [
      { id: 'JC-2026-0048', vehicle: 'VH-0112 (Volvo FM400)', estCost: 'OMR 450', parts: 'Turbocharger Core', days: '2 days open', lead: 'Rajesh K.' },
      { id: 'JC-2026-0049', vehicle: 'VH-0094 (Tata 407)', estCost: 'OMR 150', parts: 'Clutch Assembly', days: '1 day open', lead: 'Suresh P.' }
    ],
    inProgress: [
      { id: 'JC-2026-0042', vehicle: 'VH-0104 (Volvo FH16)', bay: 'Bay 1', tech: 'Rajesh Kumar', progress: 75, target: '16:30 Today' },
      { id: 'JC-2026-0039', vehicle: 'VH-0089 (Tata Prima)', bay: 'Bay 2', tech: 'Suresh Patil', progress: 45, target: 'Tomorrow' },
      { id: 'JC-2026-0045', vehicle: 'VH-0211 (BharatBenz)', bay: 'Bay 3', tech: 'Amit Verma', progress: 90, target: '14:00 Today' },
      { id: 'JC-2026-0046', vehicle: 'VH-0340 (Eicher Pro)', bay: 'Bay 5', tech: 'Vikram Singh', progress: 60, target: '17:00 Today' }
    ],
    waitingParts: [
      { id: 'JC-2026-0041', vehicle: 'VH-0072 (Scania G410)', partMissing: 'ECM Sensor Module', supplier: 'AutoSpares Hub', eta: 'Tomorrow 10 AM' },
      { id: 'JC-2026-0044', vehicle: 'VH-0220 (Tata Ultra)', partMissing: 'Hydraulic Seal Kit', supplier: 'FleetParts Direct', eta: 'Sep 23' }
    ],
    qcRelease: [
      { id: 'JC-2026-0038', vehicle: 'VH-0199 (Ashok Leyland)', qcBy: 'Mahesh Joshi (Advisor)', checklist: '14/14 Checked', ready: true },
      { id: 'JC-2026-0035', vehicle: 'VH-0182 (Tata Prima)', qcBy: 'Mahesh Joshi (Advisor)', checklist: '14/14 Checked', ready: true }
    ]
  };

  const technicians = [
    { name: 'Rajesh Kumar', role: 'Senior Technician', spec: 'Engine & Powertrain', load: '7.5 / 8.0 hrs', status: 'Occupied (Bay 1)', rate: 'OMR 18/hr' },
    { name: 'Amit Verma', role: 'Technician', spec: 'Electrical & Sensors', load: '6.0 / 8.0 hrs', status: 'Occupied (Bay 3)', rate: 'OMR 15/hr' },
    { name: 'Suresh Patil', role: 'Technician', spec: 'Bodywork & Paint', load: '5.5 / 8.0 hrs', status: 'Occupied (Bay 2)', rate: 'OMR 14/hr' },
    { name: 'Vikram Singh', role: 'Technician', spec: 'Tyres & Suspension', load: '6.5 / 8.0 hrs', status: 'Occupied (Bay 5)', rate: 'OMR 14/hr' },
    { name: 'Naveen Rao', role: 'Junior Technician', spec: 'General Inspection', load: '3.0 / 8.0 hrs', status: 'Available', rate: 'OMR 10/hr' }
  ];

  useEffect(() => {
    // Chart 1: Service Type Breakdown
    const ctx1 = document.getElementById('serviceTypeChart');
    if (ctx1) {
      const existing1 = Chart.getChart('serviceTypeChart');
      if (existing1) existing1.destroy();

      new Chart('serviceTypeChart', {
        type: 'doughnut',
        data: {
          labels: ['Scheduled Service', 'Breakdown Repair', 'Accident / Body', 'Rental Return QA', 'Tyres & Alignment'],
          datasets: [{
            data: [38, 26, 16, 12, 8],
            backgroundColor: ['#1A56DB', '#EF4444', '#F59E0B', '#10B981', '#8B5CF6'],
            borderWidth: 2,
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
              labels: { boxWidth: 10, padding: 8, font: { size: 11, family: "'Inter', sans-serif" } }
            }
          }
        }
      });
    }

    // Chart 2: Daily Bay Output Trend
    const ctx2 = document.getElementById('bayThroughputChart');
    if (ctx2) {
      const existing2 = Chart.getChart('bayThroughputChart');
      if (existing2) existing2.destroy();

      new Chart('bayThroughputChart', {
        type: 'bar',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today'],
          datasets: [
            {
              label: 'Completed Jobs',
              data: [8, 11, 9, 14, 12, 10, 6],
              backgroundColor: '#10B981',
              borderRadius: 4
            },
            {
              label: 'Vehicles In Intake',
              data: [10, 8, 12, 11, 15, 9, 7],
              backgroundColor: '#1A56DB',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: '#E2E8F0' }, beginAtZero: true }
          },
          plugins: {
            legend: {
              position: 'top',
              labels: { boxWidth: 10, font: { size: 11 } }
            }
          }
        }
      });
    }
  }, []);

  const filteredBays = selectedBayType === 'All' 
    ? bays 
    : bays.filter(b => b.type.toLowerCase().includes(selectedBayType.toLowerCase()));

  return (
    <div className="main-layout" style={{ flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div className="page-header" style={{ marginBottom: '0' }}>
        <div>
          <h1>Workshop Operations Centre</h1>
          <p>Real-time vehicle intake, bay allocation, job card progress, and technician dispatch</p>
        </div>
        <div className="header-right">
          <span className="period-pill">Today: Live Floor</span>
          <select 
            className="filter-select"
            value={selectedBayType}
            onChange={(e) => setSelectedBayType(e.target.value)}
          >
            <option value="All">All Bay Types</option>
            <option value="General Repair">General Repair</option>
            <option value="Body Shop">Body Shop</option>
            <option value="Electrical">Electrical</option>
            <option value="Tyres">Tyres & Brakes</option>
            <option value="Wash Bay">Wash & Detailing</option>
          </select>
          <button 
            className="topbar-btn primary" 
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: '20px' }}
            onClick={() => alert('New Workshop Inspection modal or flow triggered')}
          >
            <Plus size={15} /> New Inspection
          </button>
        </div>
      </div>

      {/* Top Counters - Strict Row-Wise Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: '12px', width: '100%' }}>
        {kpis.map((kpi, idx) => (
          <div key={idx} className={`kpi ${kpi.type}`} style={{ padding: '14px 16px' }}>
            <div className="kpi-label">{kpi.label}</div>
            <div className="kpi-value">{kpi.value}</div>
            <div className="kpi-sub">
              {kpi.sub}
            </div>
            <div className="kpi-icon">{kpi.icon}</div>
          </div>
        ))}
      </div>

      {/* Workshop Bay Floor Visualizer - Row-wise, Single-View Non-Scrollable */}
      <div style={{ width: '100%', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ fontSize: '12px', fontWeight: '700', letterSpacing: '.8px', textTransform: 'uppercase', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
              Live Workshop Bay Status (5/6 Occupied)
            </div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '14px', fontSize: '11.5px', background: '#fff', padding: '4px 12px', borderRadius: '20px', border: '1px solid var(--border)', boxShadow: 'var(--shadow)', whiteSpace: 'nowrap' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#EF4444' }}></span> Occupied
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#10B981' }}></span> Available
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#F59E0B' }}></span> Lift In-Use
              </span>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, minmax(0, 1fr))', gap: '10px', width: '100%', overflow: 'hidden' }}>
          {filteredBays.map((bay) => (
            <div 
              key={bay.id} 
              style={{
                minWidth: 0,
                background: '#fff',
                border: '1px solid var(--border)',
                borderTop: bay.status === 'Occupied' ? '3px solid #EF4444' : '3px solid #10B981',
                borderRadius: '8px',
                padding: '10px 8px',
                boxShadow: 'var(--shadow)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '6px'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--muted)', textTransform: 'uppercase' }}>
                    {bay.id}
                  </span>
                  <div style={{ display: 'flex', gap: '3px', alignItems: 'center' }}>
                    {bay.hasLift && (
                      <span 
                        style={{ 
                          fontSize: '10px', 
                          padding: '1px 4px', 
                          borderRadius: '3px', 
                          background: '#FEF3C7', 
                          color: '#B45309', 
                          fontWeight: '700' 
                        }}
                        title="Lift Available"
                      >
                        Lift
                      </span>
                    )}
                    <span 
                      style={{
                        fontSize: '10.5px',
                        fontWeight: '700',
                        padding: '1px 6px',
                        borderRadius: '8px',
                        backgroundColor: bay.status === 'Occupied' ? '#FEE8EA' : '#E6F7F2',
                        color: bay.status === 'Occupied' ? '#BE1D2C' : '#0A7A55'
                      }}
                    >
                      {bay.status}
                    </span>
                  </div>
                </div>

                <div style={{ fontSize: '12.5px', fontWeight: '700', color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={bay.name}>
                  {bay.name}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {bay.type}
                </div>

                {bay.status === 'Occupied' ? (
                  <div style={{ padding: '6px 8px', background: 'var(--surface)', borderRadius: '6px', marginBottom: '4px' }}>
                    <div style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--blue)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={bay.vehicle}>
                      {bay.vehicle}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {bay.jobCard}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--ink-2)', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={bay.issue}>
                      {bay.issue}
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '14px 4px', textAlign: 'center', color: 'var(--green)' }}>
                    <CheckCircle2 size={20} color="#10B981" style={{ margin: '0 auto 2px' }} />
                    <div style={{ fontSize: '12px', fontWeight: '700' }}>Ready</div>
                    <div style={{ fontSize: '11px', color: 'var(--muted)' }}>Available</div>
                  </div>
                )}
              </div>

              {bay.status === 'Occupied' && (
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--muted)', display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '60%' }}>{bay.technician.split(' ')[0]} {bay.technician.split(' ')[1]?.[0]}.</span>
                    <span style={{ whiteSpace: 'nowrap' }}>{bay.eta.replace('Today, ', '')}</span>
                  </div>
                  <div style={{ width: '100%', height: '4px', background: '#E2E8F0', borderRadius: '2px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        width: `${bay.progress}%`, 
                        height: '100%', 
                        background: bay.progress > 80 ? '#10B981' : '#1A56DB', 
                        transition: 'width 0.3s' 
                      }} 
                    />
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '10.5px', color: 'var(--muted)', marginTop: '2px', fontWeight: '600' }}>
                    {bay.progress}%
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Live Job Card Pipeline - Row-wise 5-Column Grid, Non-Scrollable */}
      <div style={{ width: '100%', overflow: 'hidden' }}>
        <div className="section-label" style={{ margin: '0 0 12px 0' }}>Live Workshop Job Pipeline</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: '10px', width: '100%', overflow: 'hidden' }}>
          
          {/* Col 1: Intake & Inspections */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11.5px' }}>
              Intake & Insp. <span className="p-count blue">{pipeline.intake.length}</span>
            </div>
            {pipeline.intake.map((item, i) => (
              <div key={i} className="job-card" style={{ padding: '8px 10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span className={`seg-pill ${item.critical ? 'cfs' : ''}`} style={{ fontSize: '10.5px', padding: '1px 6px', margin: 0 }}>{item.type}</span>
                  <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{item.date}</span>
                </div>
                <div className="job-card-no" style={{ fontSize: '11.5px' }}>{item.id}</div>
                <div className="job-card-cust" style={{ fontSize: '12px' }}>{item.vehicle}</div>
                <div className="job-card-meta" style={{ fontSize: '11px', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Inspector: {item.inspector}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                  <span style={{ fontSize: '11.5px', fontWeight: '600', color: item.status === 'Draft' ? 'var(--amber)' : 'var(--blue)' }}>
                    {item.status}
                  </span>
                  <button 
                    style={{ 
                      background: 'none', 
                      border: '1px solid var(--border)', 
                      borderRadius: '4px', 
                      padding: '2px 6px', 
                      fontSize: '10.5px', 
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '2px'
                    }}
                    onClick={() => alert(`Create Job Card for ${item.id}`)}
                  >
                    Create JC <ArrowUpRight size={10} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Col 2: Pending Approval */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11.5px' }}>
              Pending Approval <span className="p-count amber">{pipeline.pendingApproval.length}</span>
            </div>
            {pipeline.pendingApproval.map((item, i) => (
              <div key={i} className="job-card" style={{ padding: '8px 10px' }}>
                <div className="seg-pill" style={{ fontSize: '10.5px', padding: '1px 6px', marginBottom: '4px' }}>Awaiting Cost Approval</div>
                <div className="job-card-no" style={{ fontSize: '11.5px' }}>{item.id}</div>
                <div className="job-card-cust" style={{ fontSize: '12px' }}>{item.vehicle}</div>
                <div className="job-card-meta" style={{ fontSize: '11px', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Parts: {item.parts}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', paddingTop: '4px', borderTop: '1px dashed var(--border)' }}>
                  <div>
                    <div style={{ fontSize: '10.5px', color: 'var(--muted)' }}>Est. Amount</div>
                    <div style={{ fontWeight: '700', fontSize: '12px', color: 'var(--ink)' }}>{item.estCost}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '10.5px', color: 'var(--muted)' }}>Age</div>
                    <div style={{ fontSize: '11px', color: 'var(--amber)', fontWeight: '600' }}>{item.days}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Col 3: In Progress (Active) */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11.5px' }}>
              Active in Bay <span className="p-count ink">{pipeline.inProgress.length}</span>
            </div>
            {pipeline.inProgress.map((item, i) => (
              <div key={i} className="job-card" style={{ padding: '8px 10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span className="seg-pill air" style={{ fontSize: '10.5px', padding: '1px 6px', margin: 0 }}>{item.bay}</span>
                  <span style={{ fontSize: '11.5px', fontWeight: '700', color: 'var(--blue)' }}>{item.progress}%</span>
                </div>
                <div className="job-card-no" style={{ fontSize: '11.5px' }}>{item.id}</div>
                <div className="job-card-cust" style={{ fontSize: '12px' }}>{item.vehicle}</div>
                <div className="job-card-meta" style={{ fontSize: '11px', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Tech: {item.tech}</div>
                <div className="job-card-days ok" style={{ marginTop: '4px', fontSize: '10.5px', padding: '2px 5px' }}>Target: {item.target}</div>
              </div>
            ))}
          </div>

          {/* Col 4: Pending Parts / External */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11.5px' }}>
              Waiting on Parts <span className="p-count red">{pipeline.waitingParts.length}</span>
            </div>
            {pipeline.waitingParts.map((item, i) => (
              <div key={i} className="job-card" style={{ padding: '8px 10px' }}>
                <span className="seg-pill" style={{ background: '#FEE8EA', color: '#BE1D2C', fontSize: '10.5px', padding: '1px 6px', marginBottom: '4px' }}>Blocked Spares</span>
                <div className="job-card-no" style={{ fontSize: '11.5px' }}>{item.id}</div>
                <div className="job-card-cust" style={{ fontSize: '12px' }}>{item.vehicle}</div>
                <div className="job-card-meta" style={{ color: 'var(--red)', fontWeight: '600', fontSize: '11px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Part: {item.partMissing}</div>
                <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Vendor: {item.supplier}</div>
                <div className="job-card-days delay" style={{ marginTop: '4px', fontSize: '10.5px', padding: '2px 5px' }}>ETA: {item.eta}</div>
              </div>
            ))}
          </div>

          {/* Col 5: QC & Ready for Release */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11.5px' }}>
              QC & Release <span className="p-count green">{pipeline.qcRelease.length}</span>
            </div>
            {pipeline.qcRelease.map((item, i) => (
              <div key={i} className="job-card" style={{ padding: '8px 10px' }}>
                <span className="seg-pill" style={{ background: '#E6F7F2', color: '#0A7A55', fontSize: '10.5px', padding: '1px 6px', marginBottom: '4px' }}>Release Ready</span>
                <div className="job-card-no" style={{ fontSize: '11.5px' }}>{item.id}</div>
                <div className="job-card-cust" style={{ fontSize: '12px' }}>{item.vehicle}</div>
                <div className="job-card-meta" style={{ fontSize: '11px', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>Inspector: {item.qcBy}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--green)', fontWeight: '600' }}>✓ {item.checklist}</span>
                  <button 
                    style={{ 
                      background: 'var(--green)', 
                      color: '#fff', 
                      border: 'none', 
                      borderRadius: '4px', 
                      padding: '3px 7px', 
                      fontSize: '10.5px', 
                      fontWeight: '600',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap'
                    }}
                    onClick={() => alert(`Submit Vehicle Release & Workshop Summary for ${item.id}`)}
                  >
                    Release
                  </button>
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>

      {/* Row-Wise Analytics & Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Service Category Distribution</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Breakdown by job type over the last 30 days</p>
            </div>
          </div>
          <div style={{ height: '220px', position: 'relative' }}>
            <canvas id="serviceTypeChart"></canvas>
          </div>
        </div>

        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Weekly Workshop Throughput</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Intake vs. Successfully Completed Vehicles</p>
            </div>
          </div>
          <div style={{ height: '220px', position: 'relative' }}>
            <canvas id="bayThroughputChart"></canvas>
          </div>
        </div>
      </div>

      {/* Workshop Technicians Card - Laid out Row-Wise (5 side-by-side cards) */}
      <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)', width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div>
            <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Workshop Technicians (Staff)</h3>
            <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Daily capacity utilization, specializations & active vehicle dispatches</p>
          </div>
          <span className="period-pill" style={{ fontSize: '12px', padding: '4px 10px' }}>5 Active On-Duty</span>
        </div>

        {/* 5 Technicians laid out Row-Wise */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: '12px', width: '100%' }}>
          {technicians.map((t, idx) => (
            <div 
              key={idx} 
              style={{
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid var(--border)',
                background: 'var(--surface)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '8px',
                minWidth: 0
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div 
                    style={{ 
                      width: '34px', 
                      height: '34px', 
                      borderRadius: '50%', 
                      background: 'var(--blue-lt)', 
                      color: 'var(--blue)', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      fontWeight: '700',
                      fontSize: '12.5px',
                      flexShrink: 0
                    }}
                  >
                    {t.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <span 
                    style={{
                      fontSize: '10.5px',
                      fontWeight: '600',
                      padding: '2px 6px',
                      borderRadius: '8px',
                      background: t.status.includes('Available') ? '#E6F7F2' : '#EBF2FF',
                      color: t.status.includes('Available') ? '#0A7A55' : '#1A56DB',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {t.status}
                  </span>
                </div>
                <div style={{ fontWeight: '700', fontSize: '13px', color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={t.name}>
                  {t.name}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {t.role}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--blue)', fontWeight: '600', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {t.spec}
                </div>
              </div>

              <div style={{ borderTop: '1px dashed var(--border)', paddingTop: '6px', fontSize: '11px', color: 'var(--muted)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span>Daily Load:</span>
                  <strong style={{ color: 'var(--ink)' }}>{t.load}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Rate:</span>
                  <strong style={{ color: 'var(--ink)' }}>{t.rate}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '14px', padding: '10px 14px', background: '#F8FAFC', borderRadius: '8px', border: '1px dashed #CBD5E1', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: '700', color: 'var(--ink)', whiteSpace: 'nowrap' }}>💡 Shift Advisory:</span>
          <span style={{ color: 'var(--muted)', lineHeight: '1.4' }}>
            2 vehicles pending electrical clearance. Bay 3 is scheduled to finish at 14:00. Recommend queuing VH-0145 next.
          </span>
        </div>
      </div>
    </div>
  );
}
