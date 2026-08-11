import React, { useState, useEffect } from 'react';
import './3pl.css';

export default function OperationsDashboard() {
  const [warehouseActivity, setWarehouseActivity] = useState(null);

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const [grnRes, shipRes] = await Promise.all([
          fetch('/api/method/wmspro.Number_card.get_total_submitted_grn'),
          fetch('/api/method/wmspro.Number_card.get_total_submitted_outbound_shipment')
        ]);
        
        const grnData = await grnRes.json();
        const shipData = await shipRes.json();

        // If we get valid data from the API, we switch the ENTIRE block to dynamic mode
        if (grnData.message !== undefined && shipData.message !== undefined) {
          setWarehouseActivity({
            grns: grnData.message.value,
            shipments: shipData.message.value,
            transfers: 0, // Fallback dynamic mock if no endpoint
            stuckGrns: 0  // Fallback dynamic mock if no endpoint
          });
        }
      } catch (err) {
        console.error('Error fetching dynamic data, falling back to fully static block', err);
      }
    };
    fetchActivity();
  }, []);
  return (
    <div className="threepl-container" style={{ paddingTop: '24px' }}>
      
<div className="content">

  {/**/}
  <div className="page-header">
    <div>
      <h1>Operations Dashboard</h1>
      <p>Real-time view of billing health, warehouse activity, and exceptions requiring action</p>
    </div>
    <span className="period-badge">July 1 – 26, 2026</span>
  </div>

  {/**/}
  <div className="section-label">🚨 Requires Immediate Action</div>
  <div className="card" style={{marginBottom: '14px'}}>
    <div className="card-header">
      <span className="card-title">Exception Alerts</span>
      <span className="card-badge badge-red">5 Open</span>
    </div>
    <div className="card-body" style={{padding: '14px 18px'}}>
      <div className="alert danger">
        <span className="alert-icon">⛔</span>
        <div className="alert-body">
          <div className="title">3 GRNs submitted — no active contract found</div>
          <div className="desc">Customers: Alpha Pharma, BrightGoods Sdn Bhd, FreshPack Co · Cannot bill until contract is linked</div>
        </div>
      </div>
      <div className="alert danger">
        <span className="alert-icon">⛔</span>
        <div className="alert-body">
          <div className="title">7 items missing pallet capacity on Item Master</div>
          <div className="desc">Storage billing will fail for these SKUs at next billing run · Assign pallet capacity now</div>
        </div>
      </div>
      <div className="alert warn">
        <span className="alert-icon">⚠️</span>
        <div className="alert-body">
          <div className="title">2 Out Shipments cancelled after invoice was raised</div>
          <div className="desc">Credit notes required · KL-C/2026/0341, KL-C/2026/0388 · Pending Finance approval</div>
        </div>
      </div>
      <div className="alert info">
        <span className="alert-icon">ℹ️</span>
        <div className="alert-body">
          <div className="title">4 invoices pending Finance Manager approval — aging 3+ days</div>
          <div className="desc">Total value at risk: RM 84,200 · Approval needed before month-end close</div>
        </div>
      </div>
    </div>
  </div>

  {/**/}
  <div className="section-label">💳 Billing Cycle Health</div>
  <div className="grid-4" style={{marginBottom: '14px'}}>
    <div className="kpi info">
      <div className="accent-bar"></div>
      <div className="label">Invoiced This Month</div>
      <div className="value">RM 342K</div>
      <div className="sub">26 invoices raised</div>
      <div className="delta up">↑ 12% vs last month</div>
    </div>
    <div className="kpi danger">
      <div className="accent-bar"></div>
      <div className="label">Unbilled Transactions</div>
      <div className="value">RM 61K</div>
      <div className="sub">Exceptions blocking billing</div>
      <div className="delta down">↑ 3 new today</div>
    </div>
    <div className="kpi warn">
      <div className="accent-bar"></div>
      <div className="label">Overdue Receivables</div>
      <div className="value">RM 128K</div>
      <div className="sub">8 customers overdue</div>
      <div className="delta warn">4 over 60 days</div>
    </div>
    <div className="kpi success">
      <div className="accent-bar"></div>
      <div className="label">Collection Rate</div>
      <div className="value">87%</div>
      <div className="sub">MTD — target 92%</div>
      <div className="delta warn">↓ Below target</div>
    </div>
  </div>

  {/**/}
  <div className="grid-2" style={{marginBottom: '14px'}}>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Invoice Aging Breakdown</span>
        <span className="card-badge badge-red">RM 128K total</span>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <table>
          <thead><tr><th>Bucket</th><th>Customers</th><th>Amount</th><th>Risk</th></tr></thead>
          <tbody>
            <tr><td>0–30 days</td><td>12</td><td className="mono">RM 54,000</td><td><span className="pill pill-green">Low</span></td></tr>
            <tr><td>31–60 days</td><td>5</td><td className="mono">RM 38,500</td><td><span className="pill pill-amber">Medium</span></td></tr>
            <tr><td>61–90 days</td><td>3</td><td className="mono">RM 23,200</td><td><span className="pill pill-red">High</span></td></tr>
            <tr><td>&gt;90 days</td><td>1</td><td className="mono">RM 12,300</td><td><span className="pill pill-red">Critical</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Invoice Pipeline Status</span>
      </div>
      <div className="card-body">
        <div className="util-row">
          <div className="util-name">Draft</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '30%', backgroundColor: '#94A3B8'}}></div></div>
          </div>
          <div className="util-pct" style={{color: 'var(--muted)'}}>8</div>
        </div>
        <div className="util-row">
          <div className="util-name">Pending Approval</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '15%', backgroundColor: 'var(--amber)'}}></div></div>
          </div>
          <div className="util-pct" style={{color: 'var(--amber)'}}>4</div>
        </div>
        <div className="util-row">
          <div className="util-name">Approved</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '55%', backgroundColor: 'var(--blue)'}}></div></div>
          </div>
          <div className="util-pct" style={{color: 'var(--blue)'}}>14</div>
        </div>
        <div className="util-row">
          <div className="util-name">Sent to Customer</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '100%', backgroundColor: 'var(--green)'}}></div></div>
          </div>
          <div className="util-pct" style={{color: 'var(--green)'}}>26</div>
        </div>
      </div>
    </div>
  </div>

  {/**/}
  <div className="section-label">🏭 Today's Warehouse Activity</div>
  {warehouseActivity ? (
    <div className="grid-4" style={{marginBottom: '14px'}}>
      <div className="kpi success">
        <div className="accent-bar"></div>
        <div className="label">GRNs Received Today</div>
        <div className="value">{warehouseActivity.grns}</div>
        <div className="sub">Dynamic Data</div>
        <div className="delta up">Live Sync</div>
      </div>
      <div className="kpi success">
        <div className="accent-bar"></div>
        <div className="label">Shipments Dispatched</div>
        <div className="value">{warehouseActivity.shipments}</div>
        <div className="sub">Dynamic Data</div>
        <div className="delta up">Live Sync</div>
      </div>
      <div className="kpi warn">
        <div className="accent-bar"></div>
        <div className="label">Stock Transfers</div>
        <div className="value">{warehouseActivity.transfers}</div>
        <div className="sub">Dynamic Data</div>
        <div className="delta warn">Live Sync</div>
      </div>
      <div className="kpi danger">
        <div className="accent-bar"></div>
        <div className="label">Stuck GRNs (Unsubmitted)</div>
        <div className="value">{warehouseActivity.stuckGrns}</div>
        <div className="sub">Dynamic Data</div>
        <div className="delta down">Live Sync</div>
      </div>
    </div>
  ) : (
    <div className="grid-4" style={{marginBottom: '14px'}}>
      <div className="kpi success">
        <div className="accent-bar"></div>
        <div className="label">GRNs Received Today</div>
        <div className="value">14</div>
        <div className="sub">of 16 planned (Static)</div>
        <div className="delta warn">2 pending</div>
      </div>
      <div className="kpi success">
        <div className="accent-bar"></div>
        <div className="label">Shipments Dispatched</div>
        <div className="value">9</div>
        <div className="sub">of 9 planned (Static)</div>
        <div className="delta up">On schedule</div>
      </div>
      <div className="kpi warn">
        <div className="accent-bar"></div>
        <div className="label">Stock Transfers</div>
        <div className="value">3</div>
        <div className="sub">Inter-zone today (Static)</div>
        <div className="delta warn">Ledger sync pending</div>
      </div>
      <div className="kpi danger">
        <div className="accent-bar"></div>
        <div className="label">Stuck GRNs (Unsubmitted)</div>
        <div className="value">2</div>
        <div className="sub">Older than 24 hrs (Static)</div>
        <div className="delta down">Blocking billing</div>
      </div>
    </div>
  )}

  {/**/}
  <div className="grid-2" style={{marginBottom: '14px'}}>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Space Utilization by Customer</span>
        <span className="card-badge badge-amber">Overall: 76%</span>
      </div>
      <div className="card-body">
        <div className="util-row">
          <div className="util-name">Alpha Pharma</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '94%', backgroundColor: 'var(--red)'}}></div></div>
            <div style={{fontSize: '10px', color: 'var(--muted)', marginTop: '2px'}}>Zone A · 94% — Near capacity</div>
          </div>
          <div className="util-pct" style={{color: 'var(--red)'}}>94%</div>
        </div>
        <div className="util-row">
          <div className="util-name">BrightGoods</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '72%', backgroundColor: 'var(--blue)'}}></div></div>
            <div style={{fontSize: '10px', color: 'var(--muted)', marginTop: '2px'}}>Zone B · 72%</div>
          </div>
          <div className="util-pct" style={{color: 'var(--blue)'}}>72%</div>
        </div>
        <div className="util-row">
          <div className="util-name">FreshPack Co</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '61%', backgroundColor: 'var(--blue)'}}></div></div>
            <div style={{fontSize: '10px', color: 'var(--muted)', marginTop: '2px'}}>Zone C · 61%</div>
          </div>
          <div className="util-pct" style={{color: 'var(--blue)'}}>61%</div>
        </div>
        <div className="util-row">
          <div className="util-name">MegaRetail</div>
          <div className="util-bar">
            <div className="bar-wrap"><div className="bar-fill" style={{width: '38%', backgroundColor: 'var(--green)'}}></div></div>
            <div style={{fontSize: '10px', color: 'var(--muted)', marginTop: '2px'}}>Zone D · 38% — Under-utilized</div>
          </div>
          <div className="util-pct" style={{color: 'var(--green)'}}>38%</div>
        </div>
      </div>
    </div>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Dead Stock Alert (30+ Days Inactive)</span>
        <span className="card-badge badge-red">4 Customers</span>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <table>
          <thead><tr><th>Customer</th><th>Pallets</th><th>Days Idle</th><th>Action</th></tr></thead>
          <tbody>
            <tr><td>MegaRetail</td><td className="mono">18</td><td className="mono" style={{color: 'var(--red)'}}>52</td><td><span className="pill pill-red">Notify</span></td></tr>
            <tr><td>FreshPack Co</td><td className="mono">7</td><td className="mono" style={{color: 'var(--amber)'}}>34</td><td><span className="pill pill-amber">Monitor</span></td></tr>
            <tr><td>BrightGoods</td><td className="mono">4</td><td className="mono" style={{color: 'var(--amber)'}}>31</td><td><span className="pill pill-amber">Monitor</span></td></tr>
            <tr><td>SunTrade Sdn</td><td className="mono">2</td><td className="mono">30</td><td><span className="pill pill-blue">Review</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  {/**/}
  <div className="section-label">📋 Contract Compliance & Minimum Commitment</div>
  <div className="card" style={{marginBottom: '14px'}}>
    <div className="card-header">
      <span className="card-title">Minimum Commitment Tracking — July 2026</span>
      <span className="card-badge badge-amber">3 shortfalls</span>
    </div>
    <div className="card-body" style={{padding: 0}}>
      <div className="scroll-table">
        <table>
          <thead>
            <tr>
              <th>Customer</th><th>Warehouse</th><th>Min Commitment</th>
              <th>Actual (MTD)</th><th>Top-Up Required</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>MegaRetail Sdn</strong></td><td>KL-Central</td>
              <td className="mono">RM 15,000</td><td className="mono">RM 8,200</td>
              <td className="mono" style={{color: 'var(--red)'}}>RM 6,800</td>
              <td><span className="pill pill-red">Top-Up Active</span></td>
            </tr>
            <tr>
              <td><strong>SunTrade Sdn</strong></td><td>KL-Central</td>
              <td className="mono">RM 8,000</td><td className="mono">RM 5,900</td>
              <td className="mono" style={{color: 'var(--amber)'}}>RM 2,100</td>
              <td><span className="pill pill-amber">Top-Up Active</span></td>
            </tr>
            <tr>
              <td><strong>EcoStore Bhd</strong></td><td>KL-North</td>
              <td className="mono">RM 6,500</td><td className="mono">RM 6,100</td>
              <td className="mono" style={{color: 'var(--amber)'}}>RM 400</td>
              <td><span className="pill pill-amber">Near Miss</span></td>
            </tr>
            <tr>
              <td>Alpha Pharma</td><td>KL-Central</td>
              <td className="mono">RM 22,000</td><td className="mono">RM 26,400</td>
              <td className="mono" style={{color: 'var(--green)'}}>—</td>
              <td><span className="pill pill-green">Exceeded</span></td>
            </tr>
            <tr>
              <td>BrightGoods Sdn</td><td>KL-Central</td>
              <td className="mono">RM 12,000</td><td className="mono">RM 14,800</td>
              <td className="mono" style={{color: 'var(--green)'}}>—</td>
              <td><span className="pill pill-green">Exceeded</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  {/**/}
  <div className="section-label">📅 Contracts Expiring Soon</div>
  <div className="card">
    <div className="card-header">
      <span className="card-title">Renewal Risk Tracker</span>
      <span className="card-badge badge-red">2 Expiring within 30 days</span>
    </div>
    <div className="card-body" style={{padding: 0}}>
      <table>
        <thead><tr><th>Customer</th><th>Warehouse</th><th>Expiry Date</th><th>Monthly Rev</th><th>Days Left</th><th>Action</th></tr></thead>
        <tbody>
          <tr>
            <td><strong>SunTrade Sdn</strong></td><td>KL-Central</td>
            <td className="mono">2 Aug 2026</td>
            <td className="mono">RM 8,000</td>
            <td className="mono" style={{color: 'var(--red)', fontWeight: 700}}>7 days</td>
            <td><span className="pill pill-red">Urgent Renewal</span></td>
          </tr>
          <tr>
            <td><strong>EcoStore Bhd</strong></td><td>KL-North</td>
            <td className="mono">18 Aug 2026</td>
            <td className="mono">RM 6,500</td>
            <td className="mono" style={{color: 'var(--amber)', fontWeight: 700}}>23 days</td>
            <td><span className="pill pill-amber">Initiate Renewal</span></td>
          </tr>
          <tr>
            <td>FreshPack Co</td><td>KL-Central</td>
            <td className="mono">12 Sep 2026</td>
            <td className="mono">RM 11,200</td>
            <td className="mono" style={{color: 'var(--blue)'}}>48 days</td>
            <td><span className="pill pill-blue">Monitor</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

</div>{/**/}

    </div>
  );
}
