import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';

export default function MgmtView() {
  useEffect(() => {
    const C = {
      blue:'#1A56DB', blueM:'#3B82F6', green:'#10B981', greenD:'#0A7A55',
      amber:'#F59E0B', red:'#EF4444', purple:'#8B5CF6',
      border:'#E2E8F0', muted:'#5A6A80', slate:'#94A3B8'
    };

    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#5A6A80';

    const chartIds = ['mgmtTrendChart', 'volMixChart', 'impExpBar'];
    chartIds.forEach(id => {
      const ctx = document.getElementById(id);
      if (ctx) {
        const existing = Chart.getChart(ctx);
        if (existing) existing.destroy();
      }
    });

    const m12=['Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul'];
    const rev=[1980,2100,2280,2350,2050,2190,2180,2310,2420,2590,2410,2840];
    const gp=[21.2,22.1,22.8,23.5,20.1,22.9,22.9,23.8,23.5,23.5,23.6,25.7];

    const ctx1 = document.getElementById('mgmtTrendChart');
    let chart1 = null;
    if (ctx1) {
      chart1 = new Chart(ctx1, {
        data:{labels:m12,datasets:[
          {type:'bar',label:'Revenue',data:rev,backgroundColor:C.blue+'BB',borderRadius:4,yAxisID:'y'},
          {type:'line',label:'GP%',data:gp,borderColor:C.green,backgroundColor:C.green+'18',tension:.4,pointRadius:3,pointBackgroundColor:C.green,fill:true,yAxisID:'y1',borderWidth:2}
        ]},
        options:{
          responsive: true,
          maintainAspectRatio: false,
          plugins:{legend:{display:false}},
          scales:{
            x:{grid:{display:false}},
            y:{grid:{color:C.border},ticks:{callback:v=>'OMR '+(v/1000).toFixed(0)+'K'},position:'left'},
            y1:{grid:{display:false},ticks:{callback:v=>v+'%'},position:'right',min:15,max:35}
          }
        }
      });
    }

    const ctx2 = document.getElementById('volMixChart');
    let chart2 = null;
    if (ctx2) {
      chart2 = new Chart(ctx2, {
        type:'doughnut',
        data:{labels:['FCL-IMP','FCL-EXP','AIR-IMP','AIR-EXP','LCL','CFS','Other'],datasets:[{data:[25,21,15,13,18,5,3],backgroundColor:[C.blue,C.blueM,C.purple,'#A78BFA',C.green,C.amber,C.slate],borderWidth:2,borderColor:'#fff'}]},
        options:{
          cutout:'60%',
          responsive: true,
          maintainAspectRatio: false,
          plugins:{legend:{position:'right',labels:{boxWidth:8,padding:8,font:{size:11}}}}
        }
      });
    }

    const ctx3 = document.getElementById('impExpBar');
    let chart3 = null;
    if (ctx3) {
      chart3 = new Chart(ctx3, {
        type:'bar',
        data:{labels:['Feb','Mar','Apr','May','Jun','Jul'],datasets:[
          {label:'Import',data:[1340,1430,1500,1610,1490,1760],backgroundColor:C.blue+'BB',borderRadius:3},
          {label:'Export',data:[840,880,920,980,920,1080],backgroundColor:C.green+'BB',borderRadius:3}
        ]},
        options:{
          responsive: true,
          maintainAspectRatio: false,
          plugins:{legend:{position:'top',labels:{boxWidth:8,padding:6,font:{size:11}}}},
          scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,grid:{color:C.border},ticks:{callback:v=>'OMR '+(v/1000).toFixed(0)+'K'}}}
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
          <h1>Freight Management & Executive Summary</h1>
          <p>Commercial performance, segment profitability, trade lanes, and financial trends — July 2026</p>
        </div>
        <div className="header-right">
          <span className="period-pill">MTD: July 2026</span>
          <button className="topbar-btn primary" onClick={() => alert('Exporting Board Performance Summary')}>⬇ Board Export</button>
        </div>
      </div>

      {/* Top 4 Performance Counters */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '12px', width: '100%' }}>
        <div className="kpi" style={{padding:'16px 18px'}}>
          <div className="kpi-label">Total Shipments</div>
          <div style={{fontSize:21,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--blue)',lineHeight:1.2}}>342 Jobs</div>
          <div style={{fontSize:12,fontWeight:600,color:'var(--green)',marginTop:6}}>↑ +14% vs June (300)</div>
          <div className="kpi-icon">📦</div>
        </div>
        <div className="kpi" style={{padding:'16px 18px'}}>
          <div className="kpi-label">Revenue MTD</div>
          <div style={{fontSize:21,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--blue)',lineHeight:1.2}}>OMR 2.84M</div>
          <div style={{fontSize:12,fontWeight:600,color:'var(--green)',marginTop:6}}>↑ +18% vs June (OMR 2.41M)</div>
          <div className="kpi-icon">💰</div>
        </div>
        <div className="kpi" style={{padding:'16px 18px'}}>
          <div className="kpi-label">Gross Profit Margin</div>
          <div style={{fontSize:21,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--green)',lineHeight:1.2}}>25.7%</div>
          <div style={{fontSize:12,fontWeight:600,color:'var(--green)',marginTop:6}}>↑ +2.1pp vs June (23.6%)</div>
          <div className="kpi-icon">📈</div>
        </div>
        <div className="kpi" style={{padding:'16px 18px'}}>
          <div className="kpi-label">YTD Target Progress</div>
          <div style={{fontSize:21,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--ink)',lineHeight:1.2}}>OMR 18.4M</div>
          <div style={{fontSize:12,fontWeight:600,color:'var(--blue)',marginTop:6}}>96% of OMR 19.2M Target</div>
          <div className="kpi-icon">🎯</div>
        </div>
      </div>

      {/* 12-Month Revenue & GP Trend Full-Width Card */}
      <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
        <div className="chart-card-header" style={{ marginBottom: 12 }}>
          <div>
            <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>12-Month Revenue (Bars) vs Gross Profit % (Line) Trend</h3>
            <p style={{ fontSize: '12px', color: 'var(--muted)' }}>OMR thousands — primary board-level commercial growth view</p>
          </div>
          <div className="legend-row">
            <div className="legend-item"><div className="legend-dot" style={{background:'#1A56DB'}}></div>Revenue (OMR K)</div>
            <div className="legend-item"><div className="legend-dot" style={{background:'#10B981',borderRadius:'50%'}}></div>GP% (right axis)</div>
          </div>
        </div>
        <div style={{ height: '240px', position: 'relative' }}>
          <canvas id="mgmtTrendChart"></canvas>
        </div>
      </div>

      {/* Segment Performance Scorecard & Visual Analytics Row (2-Column Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Scorecard Table */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Segment Performance Scorecard — July 2026</h3>
            <span className="period-pill" style={{ fontSize: '11px', padding: '3px 8px' }}>9 Modalities</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="scorecard" style={{ width: '100%', fontSize: '12px' }}>
              <thead><tr><th>Segment</th><th>Jobs</th><th>Revenue</th><th>GP%</th><th>Avg Days</th><th>Trend</th></tr></thead>
              <tbody>
                <tr><td><span className="badge blue">FCL-IMP</span></td><td>84</td><td>OMR 910K</td><td style={{color:'var(--green)',fontWeight:600}}>27%</td><td>12.4</td><td className="t-up">↑+8%</td></tr>
                <tr><td><span className="badge blue">FCL-EXP</span></td><td>71</td><td>OMR 740K</td><td style={{color:'var(--green)',fontWeight:600}}>24%</td><td>10.1</td><td className="t-up">↑+12%</td></tr>
                <tr><td><span className="badge purple">AIR-IMP</span></td><td>52</td><td>OMR 490K</td><td style={{color:'var(--green)',fontWeight:600}}>31%</td><td>5.2</td><td className="t-up">↑+22%</td></tr>
                <tr><td><span className="badge purple">AIR-EXP</span></td><td>44</td><td>OMR 380K</td><td style={{color:'var(--green)',fontWeight:600}}>29%</td><td>4.8</td><td className="t-up">↑+18%</td></tr>
                <tr><td><span className="badge green">LCL-IMP</span></td><td>38</td><td>OMR 148K</td><td style={{color:'var(--amber)',fontWeight:600}}>16%</td><td>9.7</td><td className="t-down">↓−3%</td></tr>
                <tr><td><span className="badge green">LCL-EXP</span></td><td>24</td><td>OMR 96K</td><td style={{color:'var(--amber)',fontWeight:600}}>14%</td><td>8.3</td><td className="t-down">↓−5%</td></tr>
                <tr><td><span className="badge amber">CFS</span></td><td>18</td><td>OMR 54K</td><td style={{color:'var(--amber)',fontWeight:600}}>18%</td><td>7.1</td><td className="t-up">↑+4%</td></tr>
                <tr><td><span className="badge amber">DO</span></td><td>8</td><td>OMR 16K</td><td style={{color:'var(--red)',fontWeight:600}}>9%</td><td>2.1</td><td className="t-down">↓−2%</td></tr>
                <tr><td><strong>Total</strong></td><td><strong>342</strong></td><td><strong>OMR 2.84M</strong></td><td style={{color:'var(--green)',fontWeight:700}}>25.7%</td><td><strong>8.9</strong></td><td className="t-up"><strong>↑+14%</strong></td></tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Two Mini Charts Side-by-Side inside a Card Container */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="chart-card" style={{ background: '#fff', padding: '16px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
            <h4 style={{ margin: '0 0 10px 0', fontSize: '13px', fontWeight: '700', color: 'var(--ink)' }}>Volume Mix by Segment</h4>
            <div style={{ height: '180px', position: 'relative' }}>
              <canvas id="volMixChart"></canvas>
            </div>
          </div>
          <div className="chart-card" style={{ background: '#fff', padding: '16px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
            <h4 style={{ margin: '0 0 10px 0', fontSize: '13px', fontWeight: '700', color: 'var(--ink)' }}>Import vs Export (6M)</h4>
            <div style={{ height: '180px', position: 'relative' }}>
              <canvas id="impExpBar"></canvas>
            </div>
          </div>
        </div>
      </div>

      {/* Operational Ratios & Top Lanes (2-Column Grid) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Operations Ratios */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Operational KPIs & SLA Adherence</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <span style={{ color: 'var(--muted)' }}>On-time delivery rate:</span>
            <strong style={{ color: 'var(--green)', fontSize: '14px' }}>87% (SLA Target 90%)</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <span style={{ color: 'var(--muted)' }}>Average Customs Clearance:</span>
            <strong>3.2 days</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <span style={{ color: 'var(--muted)' }}>Average Shipment Duration:</span>
            <strong>8.9 days</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0' }}>
            <span style={{ color: 'var(--muted)' }}>Quote to Booking Conversion:</span>
            <strong style={{ color: 'var(--blue)' }}>68%</strong>
          </div>
        </div>

        {/* Top Lanes */}
        <div style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <h3 style={{ margin: '0 0 14px 0', fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Top Trade Corridors — MTD</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--surface)', borderRadius: '4px' }}>
              <span style={{ fontWeight: 600 }}>Jebel Ali → Hamburg Port</span>
              <span className="mono" style={{ color: 'var(--blue)', fontWeight: 700 }}>42 shipments</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--surface)', borderRadius: '4px' }}>
              <span style={{ fontWeight: 600 }}>Shanghai Freezone → DXB</span>
              <span className="mono" style={{ color: 'var(--blue)', fontWeight: 700 }}>38 shipments</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--surface)', borderRadius: '4px' }}>
              <span style={{ fontWeight: 600 }}>DXB Cargo Terminal → JFK</span>
              <span className="mono" style={{ color: 'var(--blue)', fontWeight: 700 }}>29 shipments</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--surface)', borderRadius: '4px' }}>
              <span style={{ fontWeight: 600 }}>Rotterdam Gateway → Jebel Ali</span>
              <span className="mono" style={{ color: 'var(--blue)', fontWeight: 700 }}>24 shipments</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
