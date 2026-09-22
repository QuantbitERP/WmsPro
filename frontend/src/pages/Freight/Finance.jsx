import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';

export default function FinanceView() {
  useEffect(() => {
    const C = {
      blue:'#1A56DB', blueM:'#3B82F6', green:'#10B981', greenD:'#0A7A55',
      amber:'#F59E0B', red:'#EF4444', purple:'#8B5CF6',
      border:'#E2E8F0', muted:'#5A6A80', slate:'#94A3B8'
    };
    
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#5A6A80';

    const chartIds = ['revCostChart', 'gpSegChart', 'costDonut'];
    chartIds.forEach(id => {
      const ctx = document.getElementById(id);
      if (ctx) {
        const existing = Chart.getChart(ctx);
        if (existing) existing.destroy();
      }
    });

    const months6 = ['Feb','Mar','Apr','May','Jun','Jul'];
    const ctx1 = document.getElementById('revCostChart');
    let chart1 = null;
    if (ctx1) {
      chart1 = new Chart(ctx1, {
        type:'bar',
        data:{labels:months6,datasets:[
          {label:'Revenue',data:[2180,2310,2420,2590,2410,2840],backgroundColor:C.blue+'BB',borderRadius:4},
          {label:'Cost',data:[1680,1760,1850,1980,1840,2110],backgroundColor:C.red+'88',borderRadius:4},
          {label:'GP',data:[500,550,570,610,570,730],backgroundColor:C.green+'BB',borderRadius:4}
        ]},
        options:{
          responsive: true,
          maintainAspectRatio: false,
          plugins:{legend:{display:false}},
          scales:{x:{grid:{display:false}},y:{grid:{color:C.border},ticks:{callback:v=>'OMR '+(v/1000).toFixed(0)+'K'}}}
        }
      });
    }

    const ctx2 = document.getElementById('gpSegChart');
    let chart2 = null;
    if (ctx2) {
      chart2 = new Chart(ctx2, {
        type:'bar',
        data:{
          labels:['AIR-IMP','AIR-EXP','FCL-IMP','FCL-EXP','CFS','LCL-IMP','LCL-EXP','DO','CCL'],
          datasets:[{data:[31,29,27,24,18,16,14,9,7],backgroundColor:[C.green,C.green,C.green,C.green,C.amber,C.amber,C.amber,C.red,C.red],borderRadius:3}]
        },
        options:{
          indexAxis:'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins:{legend:{display:false}},
          scales:{x:{grid:{color:C.border},ticks:{callback:v=>v+'%'},max:35},y:{grid:{display:false}}}
        }
      });
    }

    const ctx3 = document.getElementById('costDonut');
    let chart3 = null;
    if (ctx3) {
      chart3 = new Chart(ctx3, {
        type:'doughnut',
        data:{
          labels:['Ocean Freight','Air Freight','Customs Duty','THC','Trucking','Agency Fees','Handling','Other'],
          datasets:[{data:[38,22,14,9,7,5,3,2],backgroundColor:[C.blue,C.purple,C.red,C.amber,C.green,'#06B6D4','#F97316',C.slate],borderWidth:2,borderColor:'#fff'}]
        },
        options:{
          cutout:'60%',
          responsive: true,
          maintainAspectRatio: false,
          plugins:{legend:{position:'right',labels:{boxWidth:8,padding:8,font:{size:11}}}}
        }
      });
    }

    return () => {
      if (chart1) chart1.destroy();
      if (chart2) chart2.destroy();
      if (chart3) chart3.destroy();
    };
  }, []);

  return (
    <div className="main-layout" style={{ flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div className="page-header" style={{ marginBottom: 0 }}>
        <div>
          <h1>Freight Finance & Profitability Overview</h1>
          <p>Revenue, carrier freight costs, gross profit margins, and accounts receivable aging — July 2026</p>
        </div>
        <div className="header-right">
          <span className="period-pill">MTD: Jul 1–29, 2026</span>
          <select className="filter-select"><option>This Month</option><option>Last Month</option><option>Q3 2026</option><option>YTD 2026</option></select>
        </div>
      </div>

      {/* Month-to-Date Performance (Row-Wise 4 Columns) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '12px', width: '100%' }}>
        <div className="kpi info"><div className="kpi-label">Revenue MTD</div><div className="kpi-value sm">OMR 2.84M</div><div className="kpi-sub"><span className="up">↑18%</span> vs Jul 2025</div><div className="kpi-icon">💵</div></div>
        <div className="kpi warning"><div className="kpi-label">Total Cost MTD</div><div className="kpi-value sm">OMR 2.11M</div><div className="kpi-sub"><span className="down">↑14%</span> cost growth</div><div className="kpi-icon">📤</div></div>
        <div className="kpi success"><div className="kpi-label">Gross Profit MTD</div><div className="kpi-value sm" style={{color:'var(--green)'}}>OMR 730K</div><div className="kpi-sub"><span className="up">25.7% GP</span> margin</div><div className="kpi-icon">📈</div></div>
        <div className="kpi danger"><div className="kpi-label">Unbilled Delivered</div><div className="kpi-value sm" style={{color:'var(--red)'}}>OMR 286K</div><div className="kpi-sub">8 jobs — invoice pending</div><div className="kpi-icon">⚠️</div></div>
      </div>

      {/* Monthly Financial Performance Full-Width Card */}
      <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
        <div className="chart-card-header" style={{ marginBottom: 12 }}>
          <div>
            <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Revenue vs Cost vs Gross Profit — Last 6 Months</h3>
            <p style={{ fontSize: '12px', color: 'var(--muted)' }}>OMR thousands monthly comparisons</p>
          </div>
          <div className="legend-row">
            <div className="legend-item"><div className="legend-dot" style={{background:'#1A56DB'}}></div>Revenue</div>
            <div className="legend-item"><div className="legend-dot" style={{background:'#EF4444'}}></div>Cost</div>
            <div className="legend-item"><div className="legend-dot" style={{background:'#10B981'}}></div>Gross Profit</div>
          </div>
        </div>
        <div style={{ height: '240px', position: 'relative' }}>
          <canvas id="revCostChart"></canvas>
        </div>
      </div>

      {/* Profitability Analysis Row (2-Column Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* GP% by Segment */}
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div className="chart-card-header" style={{ marginBottom: 12 }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Gross Profit Margin % by Segment</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Profitability benchmark across all 9 modes</p>
            </div>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>Target: 15% Min</span>
          </div>
          <div style={{ height: '260px', position: 'relative' }}>
            <canvas id="gpSegChart"></canvas>
          </div>
        </div>

        {/* Cost Category Breakdown */}
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div className="chart-card-header" style={{ marginBottom: 12 }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Direct Freight Cost Breakdown</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Carrier charges, port terminal handling, duty & transit</p>
            </div>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>OMR 2.11M Total</span>
          </div>
          <div style={{ height: '260px', position: 'relative' }}>
            <canvas id="costDonut"></canvas>
          </div>
        </div>
      </div>

      {/* Target Progress & Finance Actions Row (2-Column Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Revenue Target & GP Tracker */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Revenue Target & Margin Tracker</h3>
          <div style={{ padding: '12px 14px', background: 'var(--surface)', borderRadius: '8px', border: '1px solid var(--border)', marginBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--muted)' }}>MTD Revenue Realized:</span>
              <strong style={{ fontSize: '18px', color: 'var(--blue)', fontFamily: "'JetBrains Mono', monospace" }}>OMR 2.84M</strong>
            </div>
            <div className="prog-bar" style={{ margin: '10px 0 6px 0', height: '8px' }}><div className="prog-fill blue" style={{ width: '89%', height: '100%' }}></div></div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', color: 'var(--muted)' }}>
              <span>89% of OMR 3.2M Budget</span>
              <span style={{ color: 'var(--blue)', fontWeight: 600 }}>OMR 360K needed · 2 days remaining</span>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
            <span style={{ color: 'var(--muted)' }}>Actual Gross Profit %:</span>
            <strong style={{ color: 'var(--green)' }}>25.7% (Budget 22.0%)</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', padding: '6px 0' }}>
            <span style={{ color: 'var(--muted)' }}>Jobs Below 15% GP Threshold:</span>
            <strong style={{ color: 'var(--amber)' }}>4 shipments under review</strong>
          </div>
        </div>

        {/* Finance Actions */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Finance Team Expedited Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div className="alert-item urgent" style={{ padding: '8px 10px' }}>
              <span className="alert-icon">📄</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: '12.5px' }}>8 delivered jobs need immediate invoicing</div>
                <div className="alert-ref" style={{ fontSize: '11px' }}>OMR 286,000 revenue unbilled before month-end close</div>
              </div>
            </div>
            <div className="alert-item urgent" style={{ padding: '8px 10px' }}>
              <span className="alert-icon">💸</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: '12.5px' }}>Customs duty payment authorization needed</div>
                <div className="alert-ref" style={{ fontSize: '11px' }}>Falcon Imports — OMR 42,000 guarantee</div>
              </div>
            </div>
            <div className="alert-item warning" style={{ padding: '8px 10px' }}>
              <span className="alert-icon">⏰</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: '12.5px' }}>60+ day aging receivables follow-up</div>
                <div className="alert-ref" style={{ fontSize: '11px' }}>OMR 187K total overdue across 3 accounts</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Receivables & Aging Row (2-Column Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Top Customers Table */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Top 8 Customers — Revenue MTD</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table" style={{ width: '100%', fontSize: '12px' }}>
              <thead><tr><th>#</th><th>Customer</th><th>Revenue (OMR)</th><th>GP%</th><th>Health</th></tr></thead>
              <tbody>
                <tr><td className="mono">01</td><td>Gulf Traders LLC</td><td className="mono">482,000</td><td style={{color:'var(--green)',fontWeight:600}}>28%</td><td><span className="badge green">Healthy</span></td></tr>
                <tr><td className="mono">02</td><td>Apex Electronics</td><td className="mono">371,000</td><td style={{color:'var(--green)',fontWeight:600}}>31%</td><td><span className="badge green">Healthy</span></td></tr>
                <tr><td className="mono">03</td><td>Pharma Gulf</td><td className="mono">298,000</td><td style={{color:'var(--amber)',fontWeight:600}}>19%</td><td><span className="badge green">Healthy</span></td></tr>
                <tr><td className="mono">04</td><td>Al Madina Trading</td><td className="mono">241,000</td><td style={{color:'var(--amber)',fontWeight:600}}>17%</td><td><span className="badge amber">Watch</span></td></tr>
                <tr><td className="mono">05</td><td>Falcon Imports</td><td className="mono">198,000</td><td style={{color:'var(--red)',fontWeight:600}}>8%</td><td><span className="badge red">At Risk</span></td></tr>
                <tr><td className="mono">06</td><td>Eastern Merchants</td><td className="mono">187,000</td><td style={{color:'var(--green)',fontWeight:600}}>24%</td><td><span className="badge green">Healthy</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Invoice Aging & Accruals */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Invoice Aging — Outstanding Receivables</h3>
          <div style={{ display:'flex', justifyContent:'space-between', fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>
            <span>Total Outstanding:</span>
            <span style={{ fontWeight: 700, color: 'var(--ink)', fontFamily: "'JetBrains Mono', monospace" }}>OMR 1,248,000</span>
          </div>
          <div className="aging-strip" style={{ marginBottom: 10 }}>
            <div style={{ flex: 38, background: 'var(--green-md)' }}></div>
            <div style={{ flex: 27, background: 'var(--amber-md)' }}></div>
            <div style={{ flex: 20, background: 'var(--red-md)' }}></div>
            <div style={{ flex: 15, background: 'var(--red)' }}></div>
          </div>
          <div className="aging-labels" style={{ marginBottom: 14 }}>
            <div className="aging-label"><div className="aging-swatch" style={{ background: 'var(--green-md)' }}></div>Current (38%)</div>
            <div className="aging-label"><div className="aging-swatch" style={{ background: 'var(--amber-md)' }}></div>1-30d (27%)</div>
            <div className="aging-label"><div className="aging-swatch" style={{ background: 'var(--red-md)' }}></div>31-60d (20%)</div>
            <div className="aging-label"><div className="aging-swatch" style={{ background: 'var(--red)' }}></div>60+ (15%)</div>
          </div>

          <div style={{ borderTop: '1px solid var(--border)', paddingTop: 10 }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '12.5px', fontWeight: 600 }}>Open Carrier Accruals (Top 3)</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11.5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span className="mono">FCL-IMP-26-00302 (Ocean Freight)</span>
                <strong className="mono" style={{ color: 'var(--red)' }}>OMR 84,000 (35d)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span className="mono">AIR-EXP-26-00421 (Air Freight)</span>
                <strong className="mono" style={{ color: 'var(--amber)' }}>OMR 31,500 (18d)</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
