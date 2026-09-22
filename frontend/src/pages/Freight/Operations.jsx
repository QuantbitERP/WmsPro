import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';
import { AlertCircle, CheckCircle, Clock, Package, FileText, ArrowUpRight } from 'lucide-react';

export default function OpsView() {
  useEffect(() => {
    const C = {
      blue:'#1A56DB', blueM:'#3B82F6', green:'#10B981', greenD:'#0A7A55',
      amber:'#F59E0B', red:'#EF4444', purple:'#8B5CF6',
      border:'#E2E8F0', muted:'#5A6A80', slate:'#94A3B8'
    };

    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#5A6A80';

    const ctx = document.getElementById('segDonut');
    if (!ctx) return;
    const existing = Chart.getChart(ctx);
    if (existing) existing.destroy();

    const chartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['FCL-IMP', 'FCL-EXP', 'AIR-IMP', 'AIR-EXP', 'LCL-IMP', 'LCL-EXP', 'CFS', 'DO', 'CCL'],
        datasets: [{
          data: [84, 71, 52, 44, 38, 24, 18, 8, 3],
          backgroundColor: [C.blue, C.blueM, C.purple, '#A78BFA', C.green, '#34D399', C.amber, '#FCD34D', C.slate],
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
            labels: { boxWidth: 10, padding: 8, font: { size: 11 } }
          }
        }
      }
    });

    return () => {
      chartInstance.destroy();
    };
  }, []);

  return (
    <div className="main-layout" style={{ flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div>
          <h1>Freight Operations Centre</h1>
          <p>Live shipment job pipeline, customs clearance monitor, and daily dispatch queue</p>
        </div>
        <div className="header-right">
          <span className="period-pill">Today: Live Operations</span>
          <select className="filter-select">
            <option>All Segments</option>
            <option>FCL-EXP</option>
            <option>FCL-IMP</option>
            <option>AIR-EXP</option>
            <option>AIR-IMP</option>
            <option>LCL</option>
            <option>CFS</option>
            <option>DO</option>
          </select>
        </div>
      </div>

      {/* Live Counters - Row-Wise */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: '12px', width: '100%' }}>
        <div className="kpi info">
          <div className="kpi-label">Active Jobs</div>
          <div className="kpi-value">127</div>
          <div className="kpi-sub"><span className="up">↑12</span> vs last week</div>
          <div className="kpi-icon">📦</div>
        </div>
        <div className="kpi danger">
          <div className="kpi-label">Overdue ETA</div>
          <div className="kpi-value" style={{color:'var(--red)'}}>11</div>
          <div className="kpi-sub">ETA passed, not arrived</div>
          <div className="kpi-icon">⏰</div>
        </div>
        <div className="kpi warning">
          <div className="kpi-label">Customs Pending</div>
          <div className="kpi-value" style={{color:'var(--amber)'}}>18</div>
          <div className="kpi-sub">3 rejected · 15 under exam</div>
          <div className="kpi-icon">🛃</div>
        </div>
        <div className="kpi warning">
          <div className="kpi-label">DOs Awaiting</div>
          <div className="kpi-value" style={{color:'var(--amber)'}}>24</div>
          <div className="kpi-sub">5 expiring in 48 hrs</div>
          <div className="kpi-icon">📋</div>
        </div>
        <div className="kpi success">
          <div className="kpi-label">Delivered Today</div>
          <div className="kpi-value" style={{color:'var(--green)'}}>9</div>
          <div className="kpi-sub"><span className="up">↑3</span> vs yesterday</div>
          <div className="kpi-icon">✅</div>
        </div>
      </div>

      {/* Job Pipeline - 7 Columns in Strict Single Row Grid (No Horizontal Scrollbar) */}
      <div style={{ width: '100%', overflow: 'hidden' }}>
        <div className="section-label" style={{ margin: '0 0 12px 0' }}>Live Freight Job Pipeline</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, minmax(0, 1fr))', gap: '8px', width: '100%', overflow: 'hidden' }}>
          {/* 1. Confirmed */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>Confirmed <span className="p-count blue">8</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>FCL-EXP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-EXP-26-00341</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Gulf Traders LLC</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>JBALI → Hamburg</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ On track</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill air" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>AIR-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>AIR-IMP-26-00198</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Apex Electronics</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>FRA → DXB</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ On track</div>
            </div>
          </div>

          {/* 2. In Transit */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>In Transit <span className="p-count ink">31</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>FCL-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-IMP-26-00302</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Nile Industries</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>RTM → JBALI</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ ETA Jul 31</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill air" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>AIR-EXP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>AIR-EXP-26-00445</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Desert Rose</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>DXB → JFK</div>
              <div className="job-card-days warn" style={{ fontSize: '10px', padding: '1px 5px' }}>⚠ ETA today</div>
            </div>
          </div>

          {/* 3. Arrived */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>Arrived <span className="p-count amber">14</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>FCL-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-IMP-26-00291</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Al Madina Trading</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>ATA Jul 27</div>
              <div className="job-card-days warn" style={{ fontSize: '10px', padding: '1px 5px' }}>⚠ 2 days held</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill cfs" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>CFS</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>CFS-26-00044</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Multi Cargo Inc.</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>ATA Jul 26</div>
              <div className="job-card-days bad" style={{ fontSize: '10px', padding: '1px 5px' }}>🔴 3 days held</div>
            </div>
          </div>

          {/* 4. Customs */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>Customs <span className="p-count red">18</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>FCL-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-IMP-26-00284</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Falcon Imports</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>Duty: OMR 42K</div>
              <div className="job-card-days bad" style={{ fontSize: '10px', padding: '1px 5px' }}>🔴 REJECTED</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill air" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>AIR-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>AIR-IMP-26-00176</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Tech Solutions FZ</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>Under examination</div>
              <div className="job-card-days warn" style={{ fontSize: '10px', padding: '1px 5px' }}>⚠ Day 3</div>
            </div>
          </div>

          {/* 5. DO Issued */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>DO Issued <span className="p-count amber">24</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>DO</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>DO-26-00211</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Summit Logistics</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>Expires Jul 30</div>
              <div className="job-card-days bad" style={{ fontSize: '10px', padding: '1px 5px' }}>🔴 Due tmrw</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>FCL-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-IMP-26-00267</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Eastern Merchants</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>Expires Aug 2</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ 4 days</div>
            </div>
          </div>

          {/* 6. Out for Delivery */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>Out for Del. <span className="p-count ink">7</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill land" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>LAND</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-IMP-26-00255</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Al Barsha Factory</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>DA-26-00089</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ En route</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill air" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>AIR-IMP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>AIR-IMP-26-00150</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Smart Electronics</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>DA-26-00091</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ En route</div>
            </div>
          </div>

          {/* 7. Delivered */}
          <div className="pipeline-col" style={{ minWidth: 0, width: '100%', padding: '10px 8px' }}>
            <div className="pipeline-col-head" style={{ fontSize: '11px' }}>Delivered <span className="p-count green">9</span></div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>FCL-EXP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>FCL-EXP-26-00319</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Gulf Traders LLC</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>Delivered Jul 29</div>
              <div className="job-card-days bad" style={{ fontSize: '10px', padding: '1px 5px' }}>🔴 Uninvoiced</div>
            </div>
            <div className="job-card" style={{ padding: '8px' }}>
              <div className="seg-pill air" style={{ fontSize: '10px', padding: '1px 5px', margin: '0 0 3px' }}>AIR-EXP</div>
              <div className="job-card-no" style={{ fontSize: '11px' }}>AIR-EXP-26-00421</div>
              <div className="job-card-cust" style={{ fontSize: '12px' }}>Royal Dates Exp</div>
              <div className="job-card-meta" style={{ fontSize: '11px' }}>Delivered Jul 28</div>
              <div className="job-card-days ok" style={{ fontSize: '10px', padding: '1px 5px' }}>✓ Invoiced</div>
            </div>
          </div>
        </div>
      </div>

      {/* Row-Wise Analytics & Action Items (2-Column Grid - No Overlapping) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Volume by Segment Chart */}
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Volume by Freight Segment</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Live active shipments grouped by cargo modality</p>
            </div>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>127 Jobs Active</span>
          </div>
          <div style={{ height: '260px', position: 'relative' }}>
            <canvas id="segDonut"></canvas>
          </div>
        </div>

        {/* Priority Action Alerts Queue */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Critical & Urgent Watch Queue</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Shipments requiring expedited resolution</p>
            </div>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>8 Priority Tasks</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div className="alert-item critical" style={{ padding: '10px 12px' }}>
              <span className="alert-icon">🔴</span>
              <div>
                <div style={{ fontWeight: 600, color: 'var(--ink)', fontSize: '13px' }}>Customs rejection — respond within 24 hrs</div>
                <div className="alert-ref" style={{ fontSize: '11.5px' }}>FCL-IMP-26-00284 · Falcon Imports (OMR 42K duty)</div>
                <div className="alert-time" style={{ fontSize: '11px' }}>2 hrs ago · Action needed</div>
              </div>
            </div>
            <div className="alert-item urgent" style={{ padding: '10px 12px' }}>
              <span className="alert-icon">⚠️</span>
              <div>
                <div style={{ fontWeight: 600, color: 'var(--ink)', fontSize: '13px' }}>Delivery Order expires tomorrow</div>
                <div className="alert-ref" style={{ fontSize: '11.5px' }}>DO-26-00211 · Summit Logistics</div>
                <div className="alert-time" style={{ fontSize: '11px' }}>Due Jul 30 · Contact consignee</div>
              </div>
            </div>
            <div className="alert-item urgent" style={{ padding: '10px 12px' }}>
              <span className="alert-icon">⚠️</span>
              <div>
                <div style={{ fontWeight: 600, color: 'var(--ink)', fontSize: '13px' }}>CFS cargo held 3 days — free days exhausted</div>
                <div className="alert-ref" style={{ fontSize: '11.5px' }}>CFS-26-00044 · Multi Cargo Inc.</div>
                <div className="alert-time" style={{ fontSize: '11px' }}>Storage accruing · Escalate</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row-Wise Operational Tables (2-Column Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Today's Action Queue */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Today's Action Queue</h3>
            <span style={{ fontSize: '11.5px', color: 'var(--muted)' }}>Prioritized tasks</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div className="action-item" style={{ padding: '8px 10px' }}><div className="action-num red">1</div><div><div className="action-title" style={{ fontSize: '12.5px' }}>Customs rejection — respond within 24 hrs</div><div className="action-meta" style={{ fontSize: '11.5px' }}>Falcon Imports — OMR 42,000 duty disputed. Resubmit with corrected HS codes.</div></div></div>
            <div className="action-item" style={{ padding: '8px 10px' }}><div className="action-num red">2</div><div><div className="action-title" style={{ fontSize: '12.5px' }}>DO expires tomorrow — contact consignee immediately</div><div className="action-meta" style={{ fontSize: '11.5px' }}>DO-26-00211 valid until Jul 30. Summit Logistics not yet collected.</div></div></div>
            <div className="action-item" style={{ padding: '8px 10px' }}><div className="action-num amber">3</div><div><div className="action-title" style={{ fontSize: '12.5px' }}>8 delivered jobs not invoiced — OMR 286K pending</div><div className="action-meta" style={{ fontSize: '11.5px' }}>Finance team to issue Sales Invoices before month-end close.</div></div></div>
          </div>
        </div>

        {/* Customs Declaration Status Table */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Customs Declaration Status</h3>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>Bayan System Sync</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ fontSize: '12px', width: '100%' }}>
              <thead><tr><th>Job No</th><th>Customer</th><th>Decl. No</th><th>Dir.</th><th>Duty (OMR)</th><th>Status</th></tr></thead>
              <tbody>
                <tr><td className="mono link-cell">FCL-IMP-26-00284</td><td>Falcon Imports</td><td className="mono">CD-26-00091</td><td>IMP</td><td className="mono">42,000</td><td><span className="badge red">Rejected</span></td></tr>
                <tr><td className="mono link-cell">AIR-IMP-26-00176</td><td>Tech Solutions</td><td className="mono">CD-26-00097</td><td>IMP</td><td className="mono">18,500</td><td><span className="badge amber">Under Exam</span></td></tr>
                <tr><td className="mono link-cell">FCL-IMP-26-00291</td><td>Al Madina Trading</td><td className="mono">CD-26-00099</td><td>IMP</td><td className="mono">67,200</td><td><span className="badge blue">Submitted</span></td></tr>
                <tr><td className="mono link-cell">FCL-EXP-26-00341</td><td>Gulf Traders LLC</td><td className="mono">CD-26-00104</td><td>EXP</td><td className="mono">—</td><td><span className="badge green">Released</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
