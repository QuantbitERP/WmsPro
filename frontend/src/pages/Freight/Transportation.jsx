import React from 'react';
import { 
  BarChart, 
  Truck, 
  Bell, 
  AlertTriangle, 
  Clock, 
  Info, 
  TrendingUp, 
  FileText, 
  Fuel, 
  Wrench,
  ArrowUpRight 
} from 'lucide-react';

export default function Transportation() {
  const handlePrompt = (promptText) => {
    console.log("Prompt action triggered:", promptText);
  };

  return (
    <>
      <style>{`
        .transport-dashboard {
          padding: 24px;
          font-family: var(--font-sans);
        }
        .transport-dashboard .flex-center { display: flex; align-items: center; gap: 8px; }
        .transport-dashboard .row { display: grid; gap: 12px; margin-bottom: 12px; }
        .transport-dashboard .r4 { grid-template-columns: repeat(4, 1fr); }
        .transport-dashboard .r3 { grid-template-columns: repeat(3, 1fr); }
        .transport-dashboard .r2 { grid-template-columns: 1fr 1fr; }
        .transport-dashboard .r21 { grid-template-columns: 2fr 1fr; }
        .transport-dashboard .card { background: var(--surface-2); border: 0.5px solid var(--border); border-radius: 12px; padding: 16px; }
        .transport-dashboard .metric { background: var(--surface-1); border-radius: var(--radius); padding: 12px 14px; border: 0.5px solid var(--border); transition: transform 0.2s, box-shadow 0.2s; }
        .transport-dashboard .metric:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .transport-dashboard .metric-label { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; font-weight: 500; }
        .transport-dashboard .metric-val { font-size: 22px; font-weight: 600; color: var(--text-primary); line-height: 1; }
        .transport-dashboard .metric-sub { font-size: 11px; color: var(--text-muted); margin-top: 3px; }
        
        .transport-dashboard .metric-blue { background: rgba(37, 99, 235, 0.05); border: 1px solid rgba(37, 99, 235, 0.15); }
        .transport-dashboard .metric-blue .metric-val { color: #2563EB; }
        .transport-dashboard .metric-blue .metric-label { color: rgba(37, 99, 235, 0.85); }
        
        .transport-dashboard .metric-teal { background: rgba(13, 148, 136, 0.05); border: 1px solid rgba(13, 148, 136, 0.15); }
        .transport-dashboard .metric-teal .metric-val { color: #0D9488; }
        .transport-dashboard .metric-teal .metric-label { color: rgba(13, 148, 136, 0.85); }
        
        .transport-dashboard .metric-indigo { background: rgba(79, 70, 229, 0.05); border: 1px solid rgba(79, 70, 229, 0.15); }
        .transport-dashboard .metric-indigo .metric-val { color: #4F46E5; }
        .transport-dashboard .metric-indigo .metric-label { color: rgba(79, 70, 229, 0.85); }
        
        .transport-dashboard .metric-green { background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.15); }
        .transport-dashboard .metric-green .metric-val { color: #059669; }
        .transport-dashboard .metric-green .metric-label { color: rgba(5, 150, 105, 0.85); }
        
        .transport-dashboard .metric-amber { background: rgba(217, 119, 6, 0.05); border: 1px solid rgba(217, 119, 6, 0.15); }
        .transport-dashboard .metric-amber .metric-val { color: #D97706; }
        .transport-dashboard .metric-amber .metric-label { color: rgba(217, 119, 6, 0.85); }
        
        .transport-dashboard .metric-yellow { background: rgba(202, 138, 4, 0.05); border: 1px solid rgba(202, 138, 4, 0.15); }
        .transport-dashboard .metric-yellow .metric-val { color: #CA8A04; }
        .transport-dashboard .metric-yellow .metric-label { color: rgba(202, 138, 4, 0.85); }
        
        .transport-dashboard .metric-rose { background: rgba(225, 29, 72, 0.05); border: 1px solid rgba(225, 29, 72, 0.15); }
        .transport-dashboard .metric-rose .metric-val { color: #E11D48; }
        .transport-dashboard .metric-rose .metric-label { color: rgba(225, 29, 72, 0.85); }
        
        .transport-dashboard .metric-pink { background: rgba(219, 39, 119, 0.05); border: 1px solid rgba(219, 39, 119, 0.15); }
        .transport-dashboard .metric-pink .metric-val { color: #DB2777; }
        .transport-dashboard .metric-pink .metric-label { color: rgba(219, 39, 119, 0.85); }
        .transport-dashboard .card-title { font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
        .transport-dashboard .badge { font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 500; display: inline-block; }
        .transport-dashboard .badge-green { background: var(--bg-success); color: var(--text-success); }
        .transport-dashboard .badge-amber { background: var(--bg-warning); color: var(--text-warning); }
        .transport-dashboard .badge-red { background: var(--bg-danger); color: var(--text-danger); }
        .transport-dashboard .badge-blue { background: var(--bg-accent); color: var(--text-accent); }
        .transport-dashboard .badge-gray { background: var(--surface-1); color: var(--text-muted); border: 0.5px solid var(--border); }
        .transport-dashboard .tbl { width: 100%; border-collapse: collapse; font-size: 12px; }
        .transport-dashboard .tbl th { text-align: left; padding: 6px 8px; color: var(--text-muted); font-weight: 500; border-bottom: 0.5px solid var(--border); }
        .transport-dashboard .tbl td { padding: 7px 8px; color: var(--text-primary); border-bottom: 0.5px solid var(--border); }
        .transport-dashboard .tbl tr:last-child td { border-bottom: none; }
        .transport-dashboard .tbl tr:hover td { background: var(--surface-1); }
        .transport-dashboard .prog-bar { height: 6px; background: var(--surface-1); border-radius: 3px; overflow: hidden; margin-top: 6px; }
        .transport-dashboard .prog-fill { height: 100%; border-radius: 3px; transition: width .4s; }
        .transport-dashboard .status-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 0.5px solid var(--border); font-size: 13px; }
        .transport-dashboard .status-row:last-child { border-bottom: none; }
        .transport-dashboard .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
        .transport-dashboard .dot-green { background: #1D9E75; }
        .transport-dashboard .dot-amber { background: #EF9F27; }
        .transport-dashboard .dot-red { background: #E24B4A; }
        .transport-dashboard .dot-blue { background: #378ADD; }
        .transport-dashboard .dot-gray { background: #B4B2A9; }
        .transport-dashboard .veh-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 0.5px solid var(--border); font-size: 12px; }
        .transport-dashboard .veh-row:last-child { border-bottom: none; }
        .transport-dashboard .veh-id { font-weight: 500; min-width: 72px; color: var(--text-primary); }
        .transport-dashboard .veh-bar { flex: 1; height: 5px; background: var(--surface-1); border-radius: 3px; overflow: hidden; }
        .transport-dashboard .veh-fill { height: 100%; border-radius: 3px; }
        .transport-dashboard .veh-pct { min-width: 32px; text-align: right; color: var(--text-secondary); }
        .transport-dashboard .alert-item { display: flex; align-items: flex-start; gap: 10px; padding: 9px 0; border-bottom: 0.5px solid var(--border); font-size: 12px; }
        .transport-dashboard .alert-item:last-child { border-bottom: none; }
        .transport-dashboard .alert-icon { font-size: 15px; margin-top: 1px; }
        .transport-dashboard .alert-text { flex: 1; color: var(--text-primary); }
        .transport-dashboard .alert-meta { color: var(--text-muted); font-size: 11px; margin-top: 2px; }
        .transport-dashboard .page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
        .transport-dashboard .page-title { font-size: 18px; font-weight: 500; color: var(--text-primary); }
        .transport-dashboard .header-meta { font-size: 12px; color: var(--text-muted); }
        .transport-dashboard .section-label { font-size: 11px; font-weight: 500; color: var(--text-muted); letter-spacing: .05em; text-transform: uppercase; margin-bottom: 8px; }
        .transport-dashboard .btn-sm { font-size: 12px; padding: 4px 10px; border: 0.5px solid var(--border-strong); border-radius: var(--radius); background: transparent; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; gap: 4px; }
        .transport-dashboard .btn-sm:hover { background: var(--surface-1); }
      `}</style>

      <div className="transport-dashboard">
        <div className="page-header">
          <div>
            <div className="page-title">Transportation dashboard</div>
            <div className="header-meta">Today — 25 Aug 2026 &nbsp;·&nbsp; Freight Management Module</div>
          </div>
          <button className="btn-sm" onClick={() => handlePrompt('Show me detailed truck profitability report for this month')}>
            <BarChart size={14} /> Full report <ArrowUpRight size={12} />
          </button>
        </div>

        <div className="row r4">
          <div className="metric metric-blue">
            <div className="metric-label">Active jobs</div>
            <div className="metric-val">24</div>
            <div className="metric-sub">↑ 3 from yesterday</div>
          </div>
          <div className="metric metric-teal">
            <div className="metric-label">Vehicles on road</div>
            <div className="metric-val">18</div>
            <div className="metric-sub">of 22 total fleet</div>
          </div>
          <div className="metric metric-indigo">
            <div className="metric-label">Trips today</div>
            <div className="metric-val">31</div>
            <div className="metric-sub">27 completed · 4 active</div>
          </div>
          <div className="metric metric-green">
            <div className="metric-label">Revenue MTD</div>
            <div className="metric-val">OMR 186k</div>
            <div className="metric-sub">GP: 22.4%</div>
          </div>
        </div>

        <div className="row r4">
          <div className="metric metric-amber">
            <div className="metric-label">Customs pending</div>
            <div className="metric-val">7</div>
            <div className="metric-sub">Avg wait: 2.4 days</div>
          </div>
          <div className="metric metric-yellow">
            <div className="metric-label">POD pending</div>
            <div className="metric-val">5</div>
            <div className="metric-sub">3 overdue</div>
          </div>
          <div className="metric metric-rose">
            <div className="metric-label">Doc expiring (30d)</div>
            <div className="metric-val">4</div>
            <div className="metric-sub">Insurance · permit</div>
          </div>
          <div className="metric metric-pink">
            <div className="metric-label">Service due</div>
            <div className="metric-val">2</div>
            <div className="metric-sub">OMA-1122 · OMA-4491</div>
          </div>
        </div>

        <div className="row r21">
          <div className="card">
            <div className="card-title">
              <Truck size={16} /> Active transport jobs
            </div>
            <table className="tbl">
              <thead>
                <tr>
                  <th>Job no</th><th>Customer</th><th>Route</th><th>Vehicle</th><th>Driver</th><th>Status</th><th>ETA</th>
                </tr>
              </thead>
              <tbody>
                <tr onClick={() => handlePrompt('Show details for transport job TRN-2026-00041')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>TRN-00041</td>
                  <td>Grant Plastics</td>
                  <td>Muscat WH → Sohar Port</td>
                  <td>OMA-1234</td>
                  <td>Ahmed Al Balushi</td>
                  <td><span className="badge badge-blue">In transit</span></td>
                  <td>14:30</td>
                </tr>
                <tr onClick={() => handlePrompt('Show details for transport job TRN-2026-00042')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>TRN-00042</td>
                  <td>Al Falah Trading</td>
                  <td>Jebel Ali → Dubai WH</td>
                  <td>OMA-5566</td>
                  <td>Khalid Nasser</td>
                  <td><span className="badge badge-amber">Loading</span></td>
                  <td>16:00</td>
                </tr>
                <tr onClick={() => handlePrompt('Show details for transport job TRN-2026-00043')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>TRN-00043</td>
                  <td>Summit Traders</td>
                  <td>Dubai Airport → Abu Dhabi</td>
                  <td>OMA-7789</td>
                  <td>Mohammed Al Farsi</td>
                  <td><span className="badge badge-green">Delivered</span></td>
                  <td>Done</td>
                </tr>
                <tr onClick={() => handlePrompt('Show details for transport job TRN-2026-00044')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>TRN-00044</td>
                  <td>Gulf Chemicals</td>
                  <td>Ruwais → Jebel Ali Port</td>
                  <td>OMA-3312</td>
                  <td>Saif Al Harthi</td>
                  <td><span className="badge badge-blue">In transit</span></td>
                  <td>18:15</td>
                </tr>
                <tr onClick={() => handlePrompt('Show details for transport job TRN-2026-00045')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>TRN-00045</td>
                  <td>Khalid Industries</td>
                  <td>Sharjah Ind → Dubai Port</td>
                  <td>OMA-9901</td>
                  <td>Ali Hassan</td>
                  <td><span className="badge badge-gray">Planned</span></td>
                  <td>Tomorrow</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="card">
            <div className="card-title">
              <Bell size={16} /> Alerts
            </div>
            <div className="alert-item">
              <AlertTriangle className="alert-icon" style={{ color: 'var(--text-danger)' }} size={16} />
              <div>
                <div className="alert-text">OMA-1122 — service overdue by 340 km</div>
                <div className="alert-meta">Last service: 12 Jul 2026</div>
              </div>
            </div>
            <div className="alert-item">
              <AlertTriangle className="alert-icon" style={{ color: 'var(--text-danger)' }} size={16} />
              <div>
                <div className="alert-text">Insurance expiring — OMA-4491 in 8 days</div>
                <div className="alert-meta">Policy no: INS-2024-0092</div>
              </div>
            </div>
            <div className="alert-item">
              <Clock className="alert-icon" style={{ color: 'var(--text-warning)' }} size={16} />
              <div>
                <div className="alert-text">3 PODs pending acknowledgement &gt; 24h</div>
                <div className="alert-meta">TRN-00038 · TRN-00036 · TRN-00031</div>
              </div>
            </div>
            <div className="alert-item">
              <Clock className="alert-icon" style={{ color: 'var(--text-warning)' }} size={16} />
              <div>
                <div className="alert-text">Duty payment pending — CD-2026-00078</div>
                <div className="alert-meta">Waiting 3 days · OMR 14,200</div>
              </div>
            </div>
            <div className="alert-item">
              <Info className="alert-icon" style={{ color: 'var(--text-accent)' }} size={16} />
              <div>
                <div className="alert-text">Driver Rashid licence expiring — 30 days</div>
                <div className="alert-meta">Renew before 24 Sep 2026</div>
              </div>
            </div>
          </div>
        </div>

        <div className="row r3">
          <div className="card">
            <div className="card-title">
              <Truck size={16} /> Vehicle utilization
            </div>
            <div className="veh-row">
              <div className="veh-id">OMA-1234</div>
              <div className="veh-bar"><div className="veh-fill" style={{ width: '92%', background: '#1D9E75' }}></div></div>
              <div className="veh-pct">92%</div>
            </div>
            <div className="veh-row">
              <div className="veh-id">OMA-5566</div>
              <div className="veh-bar"><div className="veh-fill" style={{ width: '85%', background: '#1D9E75' }}></div></div>
              <div className="veh-pct">85%</div>
            </div>
            <div className="veh-row">
              <div className="veh-id">OMA-7789</div>
              <div className="veh-bar"><div className="veh-fill" style={{ width: '78%', background: '#EF9F27' }}></div></div>
              <div className="veh-pct">78%</div>
            </div>
            <div className="veh-row">
              <div className="veh-id">OMA-3312</div>
              <div className="veh-bar"><div className="veh-fill" style={{ width: '71%', background: '#EF9F27' }}></div></div>
              <div className="veh-pct">71%</div>
            </div>
            <div className="veh-row">
              <div className="veh-id">OMA-9901</div>
              <div className="veh-bar"><div className="veh-fill" style={{ width: '45%', background: '#E24B4A' }}></div></div>
              <div className="veh-pct">45%</div>
            </div>
            <div className="veh-row">
              <div className="veh-id">OMA-1122</div>
              <div className="veh-bar"><div className="veh-fill" style={{ width: '0%', background: '#B4B2A9' }}></div></div>
              <div className="veh-pct" style={{ color: 'var(--text-danger)' }}>Maint.</div>
            </div>
          </div>

          <div className="card">
            <div className="card-title">
              <BarChart size={16} /> Job status breakdown
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-green"></div><span style={{ fontSize: '13px' }}>Delivered</span></div>
              <div className="flex-center"><span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>11</span><div className="badge badge-green">46%</div></div>
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-blue"></div><span style={{ fontSize: '13px' }}>In transit</span></div>
              <div className="flex-center"><span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>6</span><div className="badge badge-blue">25%</div></div>
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-amber"></div><span style={{ fontSize: '13px' }}>Customs pending</span></div>
              <div className="flex-center"><span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>4</span><div className="badge badge-amber">17%</div></div>
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-amber"></div><span style={{ fontSize: '13px' }}>Loading</span></div>
              <div className="flex-center"><span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>2</span><div className="badge badge-amber">8%</div></div>
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-gray"></div><span style={{ fontSize: '13px' }}>Planned</span></div>
              <div className="flex-center"><span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>1</span><div className="badge badge-gray">4%</div></div>
            </div>
          </div>

          <div className="card">
            <div className="card-title">
              <TrendingUp size={16} /> Top routes — MTD
            </div>
            <table className="tbl">
              <thead><tr><th>Route</th><th style={{ textAlign: 'right' }}>Trips</th><th style={{ textAlign: 'right' }}>GP%</th></tr></thead>
              <tbody>
                <tr onClick={() => handlePrompt('Show route analysis for Muscat WH to Sohar Port')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>Muscat → Sohar</td>
                  <td style={{ textAlign: 'right' }}>48</td>
                  <td style={{ textAlign: 'right', color: 'var(--text-success)' }}>28%</td>
                </tr>
                <tr onClick={() => handlePrompt('Show route analysis for Jebel Ali to Dubai WH')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>Jebel Ali → Dubai</td>
                  <td style={{ textAlign: 'right' }}>36</td>
                  <td style={{ textAlign: 'right', color: 'var(--text-success)' }}>24%</td>
                </tr>
                <tr onClick={() => handlePrompt('Show route analysis for Dubai Airport to Abu Dhabi')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>Dubai Airport → AUH</td>
                  <td style={{ textAlign: 'right' }}>22</td>
                  <td style={{ textAlign: 'right', color: 'var(--text-warning)' }}>18%</td>
                </tr>
                <tr onClick={() => handlePrompt('Show route analysis for Ruwais to Jebel Ali Port')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>Ruwais → Jebel Ali</td>
                  <td style={{ textAlign: 'right' }}>19</td>
                  <td style={{ textAlign: 'right', color: 'var(--text-success)' }}>31%</td>
                </tr>
                <tr onClick={() => handlePrompt('Show route analysis for Sharjah Industrial to Dubai Port')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>Sharjah → Dubai Port</td>
                  <td style={{ textAlign: 'right' }}>14</td>
                  <td style={{ textAlign: 'right', color: 'var(--text-danger)' }}>11%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="row r3">
          <div className="card">
            <div className="card-title">
              <FileText size={16} /> Freight jobs pending action
            </div>
            <table className="tbl">
              <thead><tr><th>Job</th><th>Customer</th><th>Next action</th></tr></thead>
              <tbody>
                <tr onClick={() => handlePrompt('Open freight job FJ-2026-00088 and show pending customs declaration')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>FJ-00088</td><td>Grant Plastics</td><td><span className="badge badge-amber">Create customs decl.</span></td>
                </tr>
                <tr onClick={() => handlePrompt('Open freight job FJ-2026-00085 and show duty payment pending')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>FJ-00085</td><td>Al Falah Trading</td><td><span className="badge badge-amber">Create duty payment</span></td>
                </tr>
                <tr onClick={() => handlePrompt('Open freight job FJ-2026-00081 and show delivery order pending')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>FJ-00081</td><td>Summit Traders</td><td><span className="badge badge-blue">Create delivery order</span></td>
                </tr>
                <tr onClick={() => handlePrompt('Open freight job FJ-2026-00079 and show cost sheet')} style={{ cursor: 'pointer' }}>
                  <td style={{ color: 'var(--text-accent)' }}>FJ-00079</td><td>Gulf Chemicals</td><td><span className="badge badge-green">Review cost sheet</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="card">
            <div className="card-title">
              <Fuel size={16} /> Fuel — this week
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px' }}>Total consumed</span>
              <span style={{ fontSize: '13px', fontWeight: 500 }}>3,840 L</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px' }}>Fuel cost</span>
              <span style={{ fontSize: '13px', fontWeight: 500 }}>OMR 8,448</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px' }}>Fleet avg KPL</span>
              <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-success)' }}>4.2 km/L</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px' }}>Best vehicle</span>
              <span style={{ fontSize: '13px', fontWeight: 500 }}>OMA-7789 · 5.1 km/L</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px' }}>Lowest vehicle</span>
              <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-danger)' }}>OMA-9901 · 2.8 km/L</span>
            </div>
            <button className="btn-sm" style={{ marginTop: '10px', width: '100%' }} onClick={() => handlePrompt('Show full fuel consumption report by vehicle for this month')}>
              View full report <ArrowUpRight size={12} />
            </button>
          </div>

          <div className="card">
            <div className="card-title">
              <Wrench size={16} /> Workshop status
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-red"></div><span style={{ fontSize: '13px' }}>OMA-1122</span></div>
              <span className="badge badge-amber">Under repair</span>
            </div>
            <div className="status-row">
              <div className="flex-center"><div className="dot dot-amber"></div><span style={{ fontSize: '13px' }}>OMA-4491</span></div>
              <span className="badge badge-blue">Scheduled 27 Aug</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Open job cards</span>
              <span style={{ fontSize: '13px', fontWeight: 500 }}>3</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Avg TAT this month</span>
              <span style={{ fontSize: '13px', fontWeight: 500 }}>1.8 days</span>
            </div>
            <div className="status-row">
              <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Maintenance cost MTD</span>
              <span style={{ fontSize: '13px', fontWeight: 500 }}>OMR 12,400</span>
            </div>
            <button className="btn-sm" style={{ marginTop: '10px', width: '100%' }} onClick={() => handlePrompt('Show all open workshop job cards with parts and labour breakdown')}>
              View workshop <ArrowUpRight size={12} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
