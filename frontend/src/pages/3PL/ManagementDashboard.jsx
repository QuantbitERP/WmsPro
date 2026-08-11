import React from 'react';
import './3pl.css';

export default function ManagementDashboard() {
  return (
    <div className="threepl-container" style={{ paddingTop: '24px' }}>
      
<div className="content">

  {/**/}
  <div className="page-header">
    <div>
      <h1>Business Performance Dashboard</h1>
      <p>Revenue health, customer concentration, and strategic decisions for leadership</p>
    </div>
    <span className="period-badge">July 2026 · MTD</span>
  </div>

  {/**/}
  <div className="section-label">💰 Revenue Performance</div>
  <div className="grid-4" style={{marginBottom: '14px'}}>
    <div className="kpi info">
      <div className="accent-bar"></div>
      <div className="label">Revenue MTD</div>
      <div className="value">RM 342K</div>
      <div className="sub">Target: RM 390K</div>
      <div className="delta warn">88% of target</div>
    </div>
    <div className="kpi success">
      <div className="accent-bar"></div>
      <div className="label">Projected Month-End</div>
      <div className="value">RM 395K</div>
      <div className="sub">Based on current contracts</div>
      <div className="delta up">↑ 1% above target</div>
    </div>
    <div className="kpi warn">
      <div className="accent-bar"></div>
      <div className="label">Revenue at Risk</div>
      <div className="value">RM 61K</div>
      <div className="sub">Unbilled + exceptions</div>
      <div className="delta down">Needs resolution</div>
    </div>
    <div className="kpi danger">
      <div className="accent-bar"></div>
      <div className="label">Overdue Receivables</div>
      <div className="value">RM 128K</div>
      <div className="sub">8 customers · 4 critical</div>
      <div className="delta down">37% of monthly rev</div>
    </div>
  </div>

  {/**/}
  <div className="card" style={{marginBottom: '14px'}}>
    <div className="card-header">
      <span className="card-title">Monthly Revenue Forecast vs Actual — July 2026</span>
    </div>
    <div className="card-body">
      <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--muted)', marginBottom: '6px'}}>
        <span>Actual Billed: <strong style={{color: 'var(--ink)'}}>RM 342K</strong></span>
        <span>Pending Resolution: <strong style={{color: 'var(--amber)'}}>RM 61K</strong></span>
        <span>Target: <strong style={{color: 'var(--ink)'}}>RM 390K</strong></span>
      </div>
      <div className="forecast-bar-wrap">
        <div className="forecast-bar-fill" style={{width: '58%', backgroundColor: 'var(--green)'}}>Billed: RM 342K</div>
        <div className="forecast-bar-fill" style={{width: '10%', backgroundColor: 'var(--amber)'}}>At Risk</div>
        <div className="forecast-bar-fill" style={{width: '32%', backgroundColor: 'var(--border)', color: 'var(--muted)'}}>Remaining period</div>
      </div>
      <div style={{display: 'flex', gap: '16px', marginTop: '10px', fontSize: '11px'}}>
        <span style={{display: 'flex', alignItems: 'center', gap: '5px'}}><span style={{width: '10px', height: '10px', backgroundColor: 'var(--green)', borderRadius: '2px', display: 'inline-block'}}></span>Billed & Approved</span>
        <span style={{display: 'flex', alignItems: 'center', gap: '5px'}}><span style={{width: '10px', height: '10px', backgroundColor: 'var(--amber)', borderRadius: '2px', display: 'inline-block'}}></span>Exception / At Risk</span>
        <span style={{display: 'flex', alignItems: 'center', gap: '5px'}}><span style={{width: '10px', height: '10px', backgroundColor: 'var(--border)', borderRadius: '2px', display: 'inline-block'}}></span>Remaining Period</span>
      </div>
    </div>
  </div>

  {/**/}
  <div className="section-label">👥 Customer Revenue & Concentration</div>
  <div className="grid-2" style={{marginBottom: '14px'}}>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Top Customers by Revenue — July MTD</span>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <table>
          <thead><tr><th>Customer</th><th>Revenue</th><th>% of Total</th><th>Trend</th></tr></thead>
          <tbody>
            <tr>
              <td><strong>Alpha Pharma</strong></td>
              <td className="mono">RM 84,000</td>
              <td>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <div className="bar-wrap" style={{width: '80px'}}><div className="bar-fill" style={{width: '25%', backgroundColor: 'var(--blue)'}}></div></div>
                  <span className="mono">25%</span>
                </div>
              </td>
              <td><span className="delta up">↑ 8%</span></td>
            </tr>
            <tr>
              <td><strong>BrightGoods Sdn</strong></td>
              <td className="mono">RM 61,200</td>
              <td>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <div className="bar-wrap" style={{width: '80px'}}><div className="bar-fill" style={{width: '18%', backgroundColor: 'var(--blue)'}}></div></div>
                  <span className="mono">18%</span>
                </div>
              </td>
              <td><span className="delta up">↑ 4%</span></td>
            </tr>
            <tr>
              <td><strong>FreshPack Co</strong></td>
              <td className="mono">RM 48,800</td>
              <td>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <div className="bar-wrap" style={{width: '80px'}}><div className="bar-fill" style={{width: '14%', backgroundColor: 'var(--amber)'}}></div></div>
                  <span className="mono">14%</span>
                </div>
              </td>
              <td><span className="delta warn">→ Stable</span></td>
            </tr>
            <tr>
              <td>MegaRetail Sdn</td>
              <td className="mono">RM 38,200</td>
              <td>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <div className="bar-wrap" style={{width: '80px'}}><div className="bar-fill" style={{width: '11%', backgroundColor: 'var(--red)'}}></div></div>
                  <span className="mono">11%</span>
                </div>
              </td>
              <td><span className="delta down">↓ 22%</span></td>
            </tr>
            <tr>
              <td>Others (12 customers)</td>
              <td className="mono">RM 109,800</td>
              <td>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <div className="bar-wrap" style={{width: '80px'}}><div className="bar-fill" style={{width: '32%', backgroundColor: 'var(--green)'}}></div></div>
                  <span className="mono">32%</span>
                </div>
              </td>
              <td><span className="delta up">↑ 3%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Customer Health Signals</span>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <table>
          <thead><tr><th>Customer</th><th>Contract</th><th>Volume Trend</th><th>Risk</th></tr></thead>
          <tbody>
            <tr>
              <td><strong>SunTrade Sdn</strong></td>
              <td><span className="pill pill-red">Expires 7 days</span></td>
              <td><span className="delta down">↓ 31%</span></td>
              <td><span className="card-badge badge-red">Churn Risk</span></td>
            </tr>
            <tr>
              <td><strong>MegaRetail Sdn</strong></td>
              <td><span className="pill pill-green">Active</span></td>
              <td><span className="delta down">↓ 22%</span></td>
              <td><span className="card-badge badge-amber">Watch</span></td>
            </tr>
            <tr>
              <td>EcoStore Bhd</td>
              <td><span className="pill pill-amber">Expires 23 days</span></td>
              <td><span className="delta warn">→ Flat</span></td>
              <td><span className="card-badge badge-amber">Watch</span></td>
            </tr>
            <tr>
              <td>Alpha Pharma</td>
              <td><span className="pill pill-green">Active · 8 mths</span></td>
              <td><span className="delta up">↑ 8%</span></td>
              <td><span className="card-badge badge-green">Healthy</span></td>
            </tr>
            <tr>
              <td>BrightGoods</td>
              <td><span className="pill pill-green">Active · 5 mths</span></td>
              <td><span className="delta up">↑ 4%</span></td>
              <td><span className="card-badge badge-green">Healthy</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  {/**/}
  <div className="section-label">🏭 Warehouse Utilization</div>
  <div className="grid-3" style={{marginBottom: '14px'}}>
    <div className="kpi info">
      <div className="accent-bar"></div>
      <div className="label">Overall Fill Rate</div>
      <div className="value">76%</div>
      <div className="sub">Optimal range: 70–85%</div>
      <div className="delta up">Healthy</div>
    </div>
    <div className="kpi danger">
      <div className="accent-bar"></div>
      <div className="label">Alpha Pharma Zone</div>
      <div className="value">94%</div>
      <div className="sub">Zone A · Near capacity limit</div>
      <div className="delta down">Expansion decision needed</div>
    </div>
    <div className="kpi warn">
      <div className="accent-bar"></div>
      <div className="label">Dead Stock Occupying Space</div>
      <div className="value">31 pallets</div>
      <div className="sub">Across 4 customers · 30+ days idle</div>
      <div className="delta warn">Opportunity cost: RM 9,300</div>
    </div>
  </div>

  {/**/}
  <div className="section-label">🧭 Decisions Required This Week</div>
  <div className="grid-2">
    <div className="card">
      <div className="card-header">
        <span className="card-title">Management Action Items</span>
        <span className="card-badge badge-red">5 decisions</span>
      </div>
      <div className="card-body">
        <div className="decision-row">
          <div className="decision-num">1</div>
          <div className="decision-content">
            <div className="action">Approve or escalate SunTrade renewal — expires in 7 days</div>
            <div className="reason">RM 8,000/month revenue. Volume declining 31%. Decide: renew at same rate or renegotiate minimum commitment downward.</div>
          </div>
        </div>
        <div className="decision-row">
          <div className="decision-num">2</div>
          <div className="decision-content">
            <div className="action">Approve RM 84,200 in invoices pending Finance sign-off</div>
            <div className="reason">4 invoices aging 3+ days without approval. Month-end cash flow at risk.</div>
          </div>
        </div>
        <div className="decision-row">
          <div className="decision-num">3</div>
          <div className="decision-content">
            <div className="action">Decide on Alpha Pharma Zone A capacity — at 94%</div>
            <div className="reason">Growing customer. Either expand zone allocation or discuss volume management with customer before overflow becomes a breach.</div>
          </div>
        </div>
        <div className="decision-row">
          <div className="decision-num">4</div>
          <div className="decision-content">
            <div className="action">Pursue RM 12,300 in debt over 90 days</div>
            <div className="reason">1 customer. Decide: issue final notice, engage collections, or negotiate payment plan before write-off risk.</div>
          </div>
        </div>
        <div className="decision-row">
          <div className="decision-num">5</div>
          <div className="decision-content">
            <div className="action">Charge idle storage fee or notify MegaRetail (52-day dead stock)</div>
            <div className="reason">18 pallets idle 52 days. Contract may allow idle storage surcharge. Customer relationship vs. revenue enforcement.</div>
          </div>
        </div>
      </div>
    </div>
    <div className="card">
      <div className="card-header">
        <span className="card-title">Billing Type Revenue Breakdown</span>
        <span className="card-badge badge-blue">July MTD</span>
      </div>
      <div className="card-body" style={{padding: 0}}>
        <table>
          <thead><tr><th>Billing Type</th><th>Revenue</th><th>% Mix</th><th>vs Last Month</th></tr></thead>
          <tbody>
            <tr>
              <td>Storage (Pallet)</td>
              <td className="mono">RM 168,000</td>
              <td>
                <div className="bar-wrap"><div className="bar-fill" style={{width: '49%', backgroundColor: 'var(--blue)'}}></div></div>
                <span className="mono" style={{fontSize: '11px'}}>49%</span>
              </td>
              <td><span className="delta up">↑ 6%</span></td>
            </tr>
            <tr>
              <td>Handling (In/Out)</td>
              <td className="mono">RM 98,500</td>
              <td>
                <div className="bar-wrap"><div className="bar-fill" style={{width: '29%', backgroundColor: 'var(--green)'}}></div></div>
                <span className="mono" style={{fontSize: '11px'}}>29%</span>
              </td>
              <td><span className="delta up">↑ 14%</span></td>
            </tr>
            <tr>
              <td>Fixed Monthly</td>
              <td className="mono">RM 48,200</td>
              <td>
                <div className="bar-wrap"><div className="bar-fill" style={{width: '14%', backgroundColor: 'var(--amber)'}}></div></div>
                <span className="mono" style={{fontSize: '11px'}}>14%</span>
              </td>
              <td><span className="delta warn">→ Stable</span></td>
            </tr>
            <tr>
              <td>Min. Commitment Top-Up</td>
              <td className="mono">RM 16,300</td>
              <td>
                <div className="bar-wrap"><div className="bar-fill" style={{width: '5%', backgroundColor: 'var(--red)'}}></div></div>
                <span className="mono" style={{fontSize: '11px'}}>5%</span>
              </td>
              <td><span className="delta down">3 customers</span></td>
            </tr>
            <tr>
              <td>One-Time Setup</td>
              <td className="mono">RM 11,000</td>
              <td>
                <div className="bar-wrap"><div className="bar-fill" style={{width: '3%', backgroundColor: '#94A3B8'}}></div></div>
                <span className="mono" style={{fontSize: '11px'}}>3%</span>
              </td>
              <td><span className="delta up">2 new contracts</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

</div>{/**/}

    </div>
  );
}
