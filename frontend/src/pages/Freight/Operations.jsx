import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';

export default function OpsView() {
  useEffect(() => {
    const C = {
      blue:'#1A56DB', blueM:'#3B82F6', green:'#10B981', greenD:'#0A7A55',
      amber:'#F59E0B', red:'#EF4444', purple:'#8B5CF6',
      border:'#E2E8F0', muted:'#5A6A80', slate:'#94A3B8'
    };

    const buildOps = () => {
      Chart.defaults.font.family = "'Inter', sans-serif";
      Chart.defaults.font.size = 11;
      Chart.defaults.color = '#5A6A80';

      const chart = Chart.getChart('segDonut');
      if (chart) chart.destroy();

      new Chart('segDonut', {
        type:'doughnut',
        data:{
          labels:['FCL-IMP','FCL-EXP','AIR-IMP','AIR-EXP','LCL-IMP','LCL-EXP','CFS','DO','CCL'],
          datasets:[{data:[84,71,52,44,38,24,18,8,3],backgroundColor:[C.blue,C.blueM,C.purple,'#A78BFA',C.green,'#34D399',C.amber,'#FCD34D',C.slate],borderWidth:2,borderColor:'#fff'}]
        },
        options:{cutout:'65%',plugins:{legend:{position:'bottom',labels:{boxWidth:8,padding:7,font:{size:10}}}}}
      });
    };

    const timer = setTimeout(buildOps, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <div className="main-layout">
        <div className="content">
          <div className="page-header">
            <div><h1>Operations Centre</h1><p>Live job pipeline, customs status and today's action queue</p></div>
            <div className="header-right">
              <span className="period-pill">Jul 29, 2026</span>
              <select className="filter-select"><option>All Segments</option><option>FCL-EXP</option><option>FCL-IMP</option><option>AIR-EXP</option><option>AIR-IMP</option><option>LCL</option><option>CFS</option><option>DO</option></select>
            </div>
          </div>

          <div className="section-label">Live Counters</div>
          <div className="grid-5">
            <div className="kpi info"><div className="kpi-label">Active Jobs</div><div className="kpi-value">127</div><div className="kpi-sub"><span className="up">↑12</span>&nbsp;vs last week</div><div className="kpi-icon">📦</div></div>
            <div className="kpi danger"><div className="kpi-label">Overdue ETA</div><div className="kpi-value" style={{color:'var(--red)'}}>11</div><div className="kpi-sub">ETA passed, not arrived</div><div className="kpi-icon">⏰</div></div>
            <div className="kpi warning"><div className="kpi-label">Customs Pending</div><div className="kpi-value" style={{color:'var(--amber)'}}>18</div><div className="kpi-sub">3 rejected · 15 under exam</div><div className="kpi-icon">🛃</div></div>
            <div className="kpi warning"><div className="kpi-label">DOs Awaiting</div><div className="kpi-value" style={{color:'var(--amber)'}}>24</div><div className="kpi-sub">5 expiring in 48 hrs</div><div className="kpi-icon">📋</div></div>
            <div className="kpi success"><div className="kpi-label">Delivered Today</div><div className="kpi-value" style={{color:'var(--green)'}}>9</div><div className="kpi-sub"><span className="up">↑3</span>&nbsp;vs yesterday</div><div className="kpi-icon">✅</div></div>
          </div>

          <div className="section-label">Job Pipeline</div>
          <div className="pipeline-strip">
            <div className="pipeline-col">
              <div className="pipeline-col-head">Confirmed <span className="p-count blue">8</span></div>
              <div className="job-card"><div className="seg-pill">FCL-EXP</div><div className="job-card-no">FCL-EXP-26-00341</div><div className="job-card-cust">Gulf Traders LLC</div><div className="job-card-meta">JBALI → Hamburg</div><div className="job-card-days ok">✓ On track</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-IMP</div><div className="job-card-no">AIR-IMP-26-00198</div><div className="job-card-cust">Apex Electronics</div><div className="job-card-meta">FRA → DXB</div><div className="job-card-days ok">✓ On track</div></div>
              <div className="job-card"><div className="seg-pill">LCL-IMP</div><div className="job-card-no">LCL-IMP-26-00089</div><div className="job-card-cust">Al Faris Group</div><div className="job-card-meta">SHA → DXB</div><div className="job-card-days ok">✓ 2 days</div></div>
            </div>

            <div className="pipeline-col">
              <div className="pipeline-col-head">In Transit <span className="p-count ink">31</span></div>
              <div className="job-card"><div className="seg-pill">FCL-IMP</div><div className="job-card-no">FCL-IMP-26-00302</div><div className="job-card-cust">Nile Industries</div><div className="job-card-meta">RTM → JBALI</div><div className="job-card-days ok">✓ ETA Jul 31</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-EXP</div><div className="job-card-no">AIR-EXP-26-00445</div><div className="job-card-cust">Desert Rose</div><div className="job-card-meta">DXB → JFK</div><div className="job-card-days warn">⚠ ETA today</div></div>
              <div className="job-card"><div className="seg-pill">FCL-EXP</div><div className="job-card-no">FCL-EXP-26-00298</div><div className="job-card-cust">Prime Steel</div><div className="job-card-meta">JBALI → SIN</div><div className="job-card-days ok">✓ ETA Aug 4</div></div>
            </div>

            <div className="pipeline-col">
              <div className="pipeline-col-head">Arrived <span className="p-count amber">14</span></div>
              <div className="job-card"><div className="seg-pill">FCL-IMP</div><div className="job-card-no">FCL-IMP-26-00291</div><div className="job-card-cust">Al Madina Trading</div><div className="job-card-meta">ATA Jul 27</div><div className="job-card-days warn">⚠ 2 days held</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-IMP</div><div className="job-card-no">AIR-IMP-26-00189</div><div className="job-card-cust">Pharma Gulf</div><div className="job-card-meta">ATA Jul 28</div><div className="job-card-days ok">✓ 1 day</div></div>
              <div className="job-card"><div className="seg-pill cfs">CFS</div><div className="job-card-no">CFS-26-00044</div><div className="job-card-cust">Multi Cargo Inc.</div><div className="job-card-meta">ATA Jul 26</div><div className="job-card-days bad">🔴 3 days held</div></div>
            </div>

            <div className="pipeline-col">
              <div className="pipeline-col-head">Customs <span className="p-count red">18</span></div>
              <div className="job-card"><div className="seg-pill">FCL-IMP</div><div className="job-card-no">FCL-IMP-26-00284</div><div className="job-card-cust">Falcon Imports</div><div className="job-card-meta">Duty: AED 42K</div><div className="job-card-days bad">🔴 REJECTED</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-IMP</div><div className="job-card-no">AIR-IMP-26-00176</div><div className="job-card-cust">Tech Solutions FZ</div><div className="job-card-meta">Under examination</div><div className="job-card-days warn">⚠ Day 3</div></div>
              <div className="job-card"><div className="seg-pill">LCL-IMP</div><div className="job-card-no">LCL-IMP-26-00071</div><div className="job-card-cust">Blue Ocean Trade</div><div className="job-card-meta">Docs submitted</div><div className="job-card-days ok">✓ Day 1</div></div>
            </div>

            <div className="pipeline-col">
              <div className="pipeline-col-head">DO Issued <span className="p-count amber">24</span></div>
              <div className="job-card"><div className="seg-pill">DO</div><div className="job-card-no">DO-26-00211</div><div className="job-card-cust">Summit Logistics</div><div className="job-card-meta">Expires Jul 30</div><div className="job-card-days bad">🔴 Expires tmrw</div></div>
              <div className="job-card"><div className="seg-pill">FCL-IMP</div><div className="job-card-no">FCL-IMP-26-00267</div><div className="job-card-cust">Eastern Merchants</div><div className="job-card-meta">Expires Aug 2</div><div className="job-card-days ok">✓ 4 days</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-IMP</div><div className="job-card-no">AIR-IMP-26-00163</div><div className="job-card-cust">Horizon Med</div><div className="job-card-meta">Expires Jul 31</div><div className="job-card-days warn">⚠ 2 days</div></div>
            </div>

            <div className="pipeline-col">
              <div className="pipeline-col-head">Out for Del. <span className="p-count ink">7</span></div>
              <div className="job-card"><div className="seg-pill land">LAND</div><div className="job-card-no">FCL-IMP-26-00255</div><div className="job-card-cust">Al Barsha Factory</div><div className="job-card-meta">DA-26-00089</div><div className="job-card-days ok">✓ En route</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-IMP</div><div className="job-card-no">AIR-IMP-26-00150</div><div className="job-card-cust">Smart Electronics</div><div className="job-card-meta">DA-26-00091</div><div className="job-card-days ok">✓ En route</div></div>
            </div>

            <div className="pipeline-col">
              <div className="pipeline-col-head">Delivered <span className="p-count green">9</span></div>
              <div className="job-card"><div className="seg-pill">FCL-EXP</div><div className="job-card-no">FCL-EXP-26-00319</div><div className="job-card-cust">Gulf Traders LLC</div><div className="job-card-meta">Delivered Jul 29</div><div className="job-card-days bad">🔴 Not invoiced</div></div>
              <div className="job-card"><div className="seg-pill air">AIR-EXP</div><div className="job-card-no">AIR-EXP-26-00421</div><div className="job-card-cust">Royal Dates Export</div><div className="job-card-meta">Delivered Jul 28</div><div className="job-card-days ok">✓ Invoiced</div></div>
              <div className="job-card"><div className="seg-pill">LCL-EXP</div><div className="job-card-no">LCL-EXP-26-00058</div><div className="job-card-cust">Horizon Med</div><div className="job-card-meta">Delivered Jul 29</div><div className="job-card-days warn">⚠ Draft invoice</div></div>
            </div>
          </div>

          <div className="section-label">Today's Action Queue</div>
          <div className="action-item"><div className="action-num red">1</div><div><div className="action-title">Customs rejection — respond within 24 hrs</div><div className="action-meta">Falcon Imports — AED 42,000 duty disputed. Resubmit with corrected HS codes.</div><div className="action-ref">FCL-IMP-26-00284 · CD-26-00091</div></div></div>
          <div className="action-item"><div className="action-num red">2</div><div><div className="action-title">DO expires tomorrow — contact consignee immediately</div><div className="action-meta">DO-26-00211 valid until Jul 30. Summit Logistics not yet collected.</div><div className="action-ref">DO-26-00211 · FCL-IMP-26-00278</div></div></div>
          <div className="action-item"><div className="action-num amber">3</div><div><div className="action-title">CFS cargo held 3 days — free days exhausted, storage accruing</div><div className="action-meta">Multi Cargo Inc. not responding. Escalate to agent and notify management.</div><div className="action-ref">CFS-26-00044 · 3PL-GRN-00871</div></div></div>
          <div className="action-item"><div className="action-num amber">4</div><div><div className="action-title">8 delivered jobs not invoiced — AED 286K revenue pending</div><div className="action-meta">Finance team to issue Sales Invoices before month-end close (2 working days).</div><div className="action-ref">View unbilled jobs →</div></div></div>
          <div className="action-item"><div className="action-num" style={{background:'var(--muted)'}}>5</div><div><div className="action-title">3 rate cards expiring this week — sales action needed</div><div className="action-meta">Gulf Traders LLC, Apex Electronics, Pharma Gulf. Renewal quotes to be sent.</div><div className="action-ref">Rate Card Expiry Report →</div></div></div>

          <div className="section-label">Customs Declaration Status</div>
          <table className="data-table">
            <thead><tr><th>Job No</th><th>Customer</th><th>Decl. No</th><th>Dir.</th><th>Submitted</th><th>Days</th><th>Duty (AED)</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td className="mono link-cell">FCL-IMP-26-00284</td><td>Falcon Imports</td><td className="mono">CD-26-00091</td><td>IMP</td><td>Jul 24</td><td style={{color:'var(--red)',fontWeight:700}}>5</td><td className="mono">42,000</td><td><span className="badge red">Rejected</span></td></tr>
              <tr><td className="mono link-cell">AIR-IMP-26-00176</td><td>Tech Solutions FZ</td><td className="mono">CD-26-00097</td><td>IMP</td><td>Jul 27</td><td style={{color:'var(--amber)',fontWeight:700}}>2</td><td className="mono">18,500</td><td><span className="badge amber">Under Exam</span></td></tr>
              <tr><td className="mono link-cell">FCL-IMP-26-00291</td><td>Al Madina Trading</td><td className="mono">CD-26-00099</td><td>IMP</td><td>Jul 28</td><td>1</td><td className="mono">67,200</td><td><span className="badge blue">Submitted</span></td></tr>
              <tr><td className="mono link-cell">LCL-IMP-26-00071</td><td>Blue Ocean Trade</td><td className="mono">CD-26-00101</td><td>IMP</td><td>Jul 29</td><td>0</td><td className="mono">8,400</td><td><span className="badge blue">Submitted</span></td></tr>
              <tr><td className="mono link-cell">FCL-EXP-26-00341</td><td>Gulf Traders LLC</td><td className="mono">CD-26-00104</td><td>EXP</td><td>Jul 28</td><td>1</td><td className="mono">—</td><td><span className="badge green">Released</span></td></tr>
            </tbody>
          </table>
        </div>

        {/* OPS SIDEBAR */}
        <div className="sidebar">
          <div className="sidebar-card">
            <div className="sidebar-title">Critical <span className="s-badge red">3</span></div>
            <div className="alert-item critical"><span className="alert-icon">🔴</span><div><div>Customs rejected — HS code error</div><div className="alert-ref">FCL-IMP-26-00284</div><div className="alert-time">2 hrs ago</div></div></div>
            <div className="alert-item critical"><span className="alert-icon">🔴</span><div><div>Credit limit breach — job blocked</div><div className="alert-ref">Blue Ocean Trade</div><div className="alert-time">4 hrs ago</div></div></div>
            <div className="alert-item critical"><span className="alert-icon">🔴</span><div><div>3PL sync error — CFS job</div><div className="alert-ref">CFS-26-00044</div><div className="alert-time">6 hrs ago</div></div></div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">Urgent <span className="s-badge amber">5</span></div>
            <div className="alert-item urgent"><span className="alert-icon">⚠️</span><div><div>DO expires tomorrow</div><div className="alert-ref">DO-26-00211</div><div className="alert-time">Due Jul 30</div></div></div>
            <div className="alert-item urgent"><span className="alert-icon">⚠️</span><div><div>Overdue ETA — 3 days late</div><div className="alert-ref">FCL-IMP-26-00261</div><div className="alert-time">ETA was Jul 26</div></div></div>
            <div className="alert-item urgent"><span className="alert-icon">⚠️</span><div><div>Accrual open 35 days</div><div className="alert-ref">MSC Line — CS-26-00182</div></div></div>
            <div className="alert-item urgent"><span className="alert-icon">⚠️</span><div><div>Examination day 3 — no update</div><div className="alert-ref">AIR-IMP-26-00176</div></div></div>
            <div className="alert-item urgent"><span className="alert-icon">⚠️</span><div><div>Missing HAWB — air export</div><div className="alert-ref">AIR-EXP-26-00445</div></div></div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">Info <span className="s-badge blue">4</span></div>
            <div className="alert-item warning"><span className="alert-icon">ℹ️</span><div><div>Rate card expiring in 2 days</div><div className="alert-ref">Gulf Traders LLC</div></div></div>
            <div className="alert-item warning"><span className="alert-icon">ℹ️</span><div><div>8 jobs unbilled post-delivery</div><div className="alert-ref">AED 286,000 at risk</div></div></div>
            <div className="alert-item warning"><span className="alert-icon">ℹ️</span><div><div>Vessel delay — MSC Allegra</div><div className="alert-ref">3 jobs impacted</div></div></div>
            <div className="alert-item warning"><span className="alert-icon">ℹ️</span><div><div>Bayan integration update</div><div className="alert-ref">2 declarations pending</div></div></div>
          </div>
          <div className="sidebar-card" style={{position:'relative'}}>
            <div className="sidebar-title">Volume by Segment</div>
            <div style={{position:'relative'}}>
              <canvas id="segDonut" height="160"></canvas>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
