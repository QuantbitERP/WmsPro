import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';

export default function FinanceView() {
  useEffect(() => {
    const C = {
      blue:'#1A56DB', blueM:'#3B82F6', green:'#10B981', greenD:'#0A7A55',
      amber:'#F59E0B', red:'#EF4444', purple:'#8B5CF6',
      border:'#E2E8F0', muted:'#5A6A80', slate:'#94A3B8'
    };
    
    const buildFinance = () => {
      Chart.defaults.font.family = "'Inter', sans-serif";
      Chart.defaults.font.size = 11;
      Chart.defaults.color = '#5A6A80';

      const chartIds = ['revCostChart', 'gpSegChart', 'costDonut', 'impExpChart'];
      chartIds.forEach(id => {
        const chart = Chart.getChart(id);
        if (chart) chart.destroy();
      });

      const months6 = ['Feb','Mar','Apr','May','Jun','Jul'];
      new Chart('revCostChart',{
        type:'bar',
        data:{labels:months6,datasets:[
          {label:'Revenue',data:[2180,2310,2420,2590,2410,2840],backgroundColor:C.blue+'BB',borderRadius:4},
          {label:'Cost',data:[1680,1760,1850,1980,1840,2110],backgroundColor:C.red+'88',borderRadius:4},
          {label:'GP',data:[500,550,570,610,570,730],backgroundColor:C.green+'BB',borderRadius:4}
        ]},
        options:{plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:C.border},ticks:{callback:v=>'OMR '+(v/1000).toFixed(0)+'K'}}}}
      });

      new Chart('gpSegChart',{
        type:'bar',
        data:{
          labels:['AIR-IMP','AIR-EXP','FCL-IMP','FCL-EXP','CFS','LCL-IMP','LCL-EXP','DO','CCL'],
          datasets:[{data:[31,29,27,24,18,16,14,9,7],backgroundColor:[C.green,C.green,C.green,C.green,C.amber,C.amber,C.amber,C.red,C.red],borderRadius:3}]
        },
        options:{indexAxis:'y',plugins:{legend:{display:false},annotation:{annotations:{line1:{type:'line',xMin:15,xMax:15,borderColor:C.red,borderWidth:1.5,borderDash:[4,3]}}}},scales:{x:{grid:{color:C.border},ticks:{callback:v=>v+'%'},max:40},y:{grid:{display:false}}}}
      });

      new Chart('costDonut',{
        type:'doughnut',
        data:{
          labels:['Ocean Freight','Air Freight','Customs Duty','THC','Trucking','Agency Fees','Handling','Other'],
          datasets:[{data:[38,22,14,9,7,5,3,2],backgroundColor:[C.blue,C.purple,C.red,C.amber,C.green,'#06B6D4','#F97316',C.slate],borderWidth:2,borderColor:'#fff'}]
        },
        options:{cutout:'60%',plugins:{legend:{position:'bottom',labels:{boxWidth:8,padding:6,font:{size:10}}}}}
      });

      new Chart('impExpChart',{
        type:'doughnut',
        data:{labels:['Import','Export'],datasets:[{data:[62,38],backgroundColor:[C.blue,C.green],borderWidth:2,borderColor:'#fff'}]},
        options:{cutout:'60%',plugins:{legend:{position:'bottom',labels:{boxWidth:8,padding:6}}}}
      });
    };
    
    // Slight delay to ensure DOM is ready
    const timer = setTimeout(buildFinance, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      {/* Header */}
      <div className="page-header">
        <div><h1>Finance Overview</h1><p>Revenue, cost, GP and invoice health — July 2026</p></div>
        <div className="header-right">
          <span className="period-pill">MTD: Jul 1–29, 2026</span>
          <select className="filter-select"><option>This Month</option><option>Last Month</option><option>Q3 2026</option><option>YTD 2026</option></select>
        </div>
      </div>

      <div className="main-layout">
        <div className="content">
          <div className="section-label">Month-to-Date Performance</div>
          <div className="grid-4">
            <div className="kpi info"><div className="kpi-label">Revenue MTD</div><div className="kpi-value sm">OMR 2.84M</div><div className="kpi-sub"><span className="up">↑18%</span>&nbsp;vs Jul 2025</div><div className="kpi-icon">💵</div></div>
            <div className="kpi warning"><div className="kpi-label">Total Cost MTD</div><div className="kpi-value sm">OMR 2.11M</div><div className="kpi-sub"><span className="down">↑14%</span>&nbsp;cost growth</div><div className="kpi-icon">📤</div></div>
            <div className="kpi success"><div className="kpi-label">Gross Profit MTD</div><div className="kpi-value sm" style={{color:'var(--green)'}}>OMR 730K</div><div className="kpi-sub"><span className="up">25.7% GP</span>&nbsp;margin</div><div className="kpi-icon">📈</div></div>
            <div className="kpi danger"><div className="kpi-label">Unbilled Delivered</div><div className="kpi-value sm" style={{color:'var(--red)'}}>OMR 286K</div><div className="kpi-sub">8 jobs — invoice pending</div><div className="kpi-icon">⚠️</div></div>
          </div>

          <div className="section-label">Revenue vs Cost vs Gross Profit — Last 6 Months</div>
          <div className="chart-card">
            <div className="chart-card-header">
              <div><div className="chart-card-title">Monthly Financial Performance</div><div className="chart-card-sub">OMR thousands</div></div>
              <div className="legend-row">
                <div className="legend-item"><div className="legend-dot" style={{background:'#1A56DB'}}></div>Revenue</div>
                <div className="legend-item"><div className="legend-dot" style={{background:'#EF4444'}}></div>Cost</div>
                <div className="legend-item"><div className="legend-dot" style={{background:'#10B981'}}></div>GP</div>
              </div>
            </div>
            <canvas id="revCostChart" height="90"></canvas>
          </div>

          <div className="section-label">Profitability Analysis</div>
          <div className="grid-2">
            <div className="chart-card">
              <div className="chart-card-header"><div><div className="chart-card-title">GP% by Segment</div><div className="chart-card-sub">Threshold line at 15%</div></div></div>
              <canvas id="gpSegChart" height="160"></canvas>
            </div>
            <div className="chart-card">
              <div className="chart-card-header"><div><div className="chart-card-title">Cost Category Breakdown</div><div className="chart-card-sub">Where the money goes this month</div></div></div>
              <canvas id="costDonut" height="160"></canvas>
            </div>
          </div>

          <div className="section-label">Customer Revenue & Receivables</div>
          <div className="grid-2">
            <div className="chart-card">
              <div className="chart-card-title" style={{marginBottom:12}}>Top 8 Customers — Revenue MTD</div>
              <table className="data-table">
                <thead><tr><th>#</th><th>Customer</th><th>Revenue (OMR)</th><th>GP%</th><th>Health</th></tr></thead>
                <tbody>
                  <tr><td className="mono">01</td><td>Gulf Traders LLC</td><td className="mono">482,000</td><td style={{color:'var(--green)',fontWeight:600}}>28%</td><td><span className="badge green">Healthy</span></td></tr>
                  <tr><td className="mono">02</td><td>Apex Electronics</td><td className="mono">371,000</td><td style={{color:'var(--green)',fontWeight:600}}>31%</td><td><span className="badge green">Healthy</span></td></tr>
                  <tr><td className="mono">03</td><td>Pharma Gulf</td><td className="mono">298,000</td><td style={{color:'var(--amber)',fontWeight:600}}>19%</td><td><span className="badge green">Healthy</span></td></tr>
                  <tr><td className="mono">04</td><td>Al Madina Trading</td><td className="mono">241,000</td><td style={{color:'var(--amber)',fontWeight:600}}>17%</td><td><span className="badge amber">Watch</span></td></tr>
                  <tr><td className="mono">05</td><td>Falcon Imports</td><td className="mono">198,000</td><td style={{color:'var(--red)',fontWeight:600}}>8%</td><td><span className="badge red">At Risk</span></td></tr>
                  <tr><td className="mono">06</td><td>Eastern Merchants</td><td className="mono">187,000</td><td style={{color:'var(--green)',fontWeight:600}}>24%</td><td><span className="badge green">Healthy</span></td></tr>
                  <tr><td className="mono">07</td><td>Prime Steel Co.</td><td className="mono">162,000</td><td style={{color:'var(--amber)',fontWeight:600}}>14%</td><td><span className="badge amber">Watch</span></td></tr>
                  <tr><td className="mono">08</td><td>Blue Ocean Trade</td><td className="mono">144,000</td><td style={{color:'var(--red)',fontWeight:600}}>−2%</td><td><span className="badge red">Loss</span></td></tr>
                </tbody>
              </table>
            </div>
            <div>
              <div className="chart-card" style={{marginBottom:12}}>
                <div className="chart-card-title" style={{marginBottom:10}}>Invoice Aging — Outstanding Receivables</div>
                <div style={{display:'flex',justifyContent:'space-between',fontSize:11,color:'var(--muted)',marginBottom:4}}><span>Total Outstanding</span><span style={{fontWeight:700,color:'var(--ink)',fontFamily:"'JetBrains Mono',monospace"}}>OMR 1,248,000</span></div>
                <div className="aging-strip">
                  <div style={{flex:38,background:'var(--green-md)'}}></div>
                  <div style={{flex:27,background:'var(--amber-md)'}}></div>
                  <div style={{flex:20,background:'var(--red-md)'}}></div>
                  <div style={{flex:15,background:'var(--red)'}}></div>
                </div>
                <div className="aging-labels">
                  <div className="aging-label"><div className="aging-swatch" style={{background:'var(--green-md)'}}></div>Current (OMR 474K · 38%)</div>
                  <div className="aging-label"><div className="aging-swatch" style={{background:'var(--amber-md)'}}></div>1-30d (OMR 337K · 27%)</div>
                  <div className="aging-label"><div className="aging-swatch" style={{background:'var(--red-md)'}}></div>31-60d (OMR 250K · 20%)</div>
                  <div className="aging-label"><div className="aging-swatch" style={{background:'var(--red)'}}></div>60+ (OMR 187K · 15%)</div>
                </div>
              </div>
              <div className="chart-card">
                <div className="chart-card-title" style={{marginBottom:10}}>Open Accruals — Top 5</div>
                <table className="data-table">
                  <thead><tr><th>Job</th><th>Charge</th><th>Amount</th><th>Days</th></tr></thead>
                  <tbody>
                    <tr><td className="mono link-cell">FCL-IMP-26-00302</td><td>Ocean Freight</td><td className="mono">OMR 84,000</td><td style={{color:'var(--red)',fontWeight:700}}>35</td></tr>
                    <tr><td className="mono link-cell">AIR-EXP-26-00421</td><td>Air Freight</td><td className="mono">OMR 31,500</td><td style={{color:'var(--amber)',fontWeight:700}}>18</td></tr>
                    <tr><td className="mono link-cell">FCL-EXP-26-00319</td><td>THC</td><td className="mono">OMR 12,800</td><td style={{color:'var(--amber)',fontWeight:700}}>12</td></tr>
                    <tr><td className="mono link-cell">LCL-IMP-26-00071</td><td>Customs Agency</td><td className="mono">OMR 6,200</td><td style={{color:'var(--green)',fontWeight:700}}>4</td></tr>
                    <tr><td className="mono link-cell">CFS-26-00044</td><td>Storage</td><td className="mono">OMR 4,800</td><td style={{color:'var(--green)',fontWeight:700}}>3</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div className="sidebar">
          <div className="sidebar-card">
            <div className="sidebar-title">Revenue Target</div>
            <div style={{textAlign:'center',padding:'8px 0'}}>
              <div style={{fontSize:28,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--blue)'}}>OMR 2.84M</div>
              <div style={{fontSize:11,color:'var(--muted)',marginTop:4}}>of OMR 3.2M target</div>
              <div className="prog-bar" style={{marginTop:10}}><div className="prog-fill blue" style={{width:'89%'}}></div></div>
              <div style={{fontSize:13,fontWeight:700,color:'var(--blue)',marginTop:6}}>89% achieved</div>
              <div style={{fontSize:11,color:'var(--muted)'}}>OMR 360K needed · 2 days left</div>
            </div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">GP% Tracker</div>
            <div className="metric-row"><span className="metric-label">Target GP%</span><span className="metric-val" style={{color:'var(--muted)'}}>22.0%</span></div>
            <div className="metric-row"><span className="metric-label">Actual GP%</span><span className="metric-val" style={{color:'var(--green)'}}>25.7%</span></div>
            <div className="metric-row"><span className="metric-label">Jobs below 15%</span><span className="metric-val" style={{color:'var(--red)'}}>4</span></div>
            <div className="metric-row"><span className="metric-label">Loss jobs MTD</span><span className="metric-val" style={{color:'var(--red)'}}>1</span></div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">Finance Actions</div>
            <div className="alert-item urgent"><span className="alert-icon">📄</span><div><div>8 jobs need invoicing</div><div className="alert-ref">OMR 286,000 unbilled</div></div></div>
            <div className="alert-item urgent"><span className="alert-icon">💸</span><div><div>Duty payment auth needed</div><div className="alert-ref">Falcon — OMR 42,000</div></div></div>
            <div className="alert-item warning"><span className="alert-icon">🔁</span><div><div>5 accruals to reverse</div><div className="alert-ref">PIs received, match needed</div></div></div>
            <div className="alert-item warning"><span className="alert-icon">⏰</span><div><div>60+ day outstanding</div><div className="alert-ref">OMR 187K — escalate</div></div></div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">Import vs Export</div>
            <canvas id="impExpChart" height="130"></canvas>
          </div>
        </div>
      </div>
    </>
  );
}
