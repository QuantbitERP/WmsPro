import React, { useEffect } from 'react';
import Chart from 'chart.js/auto';

export default function MgmtView() {
  useEffect(() => {
    const C = {
      blue:'#1A56DB', blueM:'#3B82F6', green:'#10B981', greenD:'#0A7A55',
      amber:'#F59E0B', red:'#EF4444', purple:'#8B5CF6',
      border:'#E2E8F0', muted:'#5A6A80', slate:'#94A3B8'
    };

    const buildMgmt = () => {
      Chart.defaults.font.family = "'Inter', sans-serif";
      Chart.defaults.font.size = 11;
      Chart.defaults.color = '#5A6A80';

      const chartIds = ['mgmtTrendChart', 'volMixChart', 'impExpBar'];
      chartIds.forEach(id => {
        const chart = Chart.getChart(id);
        if (chart) chart.destroy();
      });

      const m12=['Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul'];
      const rev=[1980,2100,2280,2350,2050,2190,2180,2310,2420,2590,2410,2840];
      const gp=[21.2,22.1,22.8,23.5,20.1,22.9,22.9,23.8,23.5,23.5,23.6,25.7];

      new Chart('mgmtTrendChart',{
        data:{labels:m12,datasets:[
          {type:'bar',label:'Revenue',data:rev,backgroundColor:C.blue+'BB',borderRadius:4,yAxisID:'y'},
          {type:'line',label:'GP%',data:gp,borderColor:C.green,backgroundColor:C.green+'18',tension:.4,pointRadius:3,pointBackgroundColor:C.green,fill:true,yAxisID:'y1',borderWidth:2}
        ]},
        options:{plugins:{legend:{display:false}},scales:{
          x:{grid:{display:false}},
          y:{grid:{color:C.border},ticks:{callback:v=>'OMR '+(v/1000).toFixed(0)+'K'},position:'left'},
          y1:{grid:{display:false},ticks:{callback:v=>v+'%'},position:'right',min:15,max:35}
        }}
      });

      new Chart('volMixChart',{
        type:'doughnut',
        data:{labels:['FCL-IMP','FCL-EXP','AIR-IMP','AIR-EXP','LCL','CFS','Other'],datasets:[{data:[25,21,15,13,18,5,3],backgroundColor:[C.blue,C.blueM,C.purple,'#A78BFA',C.green,C.amber,C.slate],borderWidth:2,borderColor:'#fff'}]},
        options:{cutout:'58%',plugins:{legend:{position:'bottom',labels:{boxWidth:8,padding:5,font:{size:10}}}}}
      });

      new Chart('impExpBar',{
        type:'bar',
        data:{labels:['Feb','Mar','Apr','May','Jun','Jul'],datasets:[
          {label:'Import',data:[1340,1430,1500,1610,1490,1760],backgroundColor:C.blue+'BB',borderRadius:3},
          {label:'Export',data:[840,880,920,980,920,1080],backgroundColor:C.green+'BB',borderRadius:3}
        ]},
        options:{plugins:{legend:{position:'bottom',labels:{boxWidth:8,padding:6}}},scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,grid:{color:C.border},ticks:{callback:v=>'OMR '+(v/1000).toFixed(0)+'K'}}}}
      });
    };

    const timer = setTimeout(buildMgmt, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <div className="main-layout">
        <div className="content">
          <div className="page-header">
            <div><h1>Management Summary</h1><p>Business health, growth and segment performance — July 2026</p></div>
            <div className="header-right">
              <span className="period-pill">July 2026</span>
              <button className="topbar-btn primary" style={{marginLeft: 8}}>⬇ Board Export</button>
            </div>
          </div>

          <div className="section-label">This Month vs Last Month</div>
          <div className="grid-3">
            <div className="kpi" style={{textAlign:'center',padding:'20px 16px'}}>
              <div className="kpi-label" style={{textAlign:'center'}}>Total Jobs</div>
              <div style={{fontSize:38,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--blue)',lineHeight:1.1}}>342</div>
              <div style={{fontSize:13,fontWeight:600,color:'var(--green)',marginTop:6}}>↑ +14% vs June</div>
              <div style={{fontSize:11,color:'var(--muted)',marginTop:3}}>Jun: 300 jobs</div>
            </div>
            <div className="kpi" style={{textAlign:'center',padding:'20px 16px'}}>
              <div className="kpi-label" style={{textAlign:'center'}}>Revenue MTD</div>
              <div style={{fontSize:38,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--blue)',lineHeight:1.1}}>2.84M</div>
              <div style={{fontSize:13,fontWeight:600,color:'var(--green)',marginTop:6}}>↑ +18% vs June</div>
              <div style={{fontSize:11,color:'var(--muted)',marginTop:3}}>Jun: OMR 2.41M</div>
            </div>
            <div className="kpi" style={{textAlign:'center',padding:'20px 16px'}}>
              <div className="kpi-label" style={{textAlign:'center'}}>Gross Profit %</div>
              <div style={{fontSize:38,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--green)',lineHeight:1.1}}>25.7%</div>
              <div style={{fontSize:13,fontWeight:600,color:'var(--green)',marginTop:6}}>↑ +2.1pp vs June</div>
              <div style={{fontSize:11,color:'var(--muted)',marginTop:3}}>Jun: 23.6%</div>
            </div>
          </div>

          <div className="section-label">12-Month Revenue & GP Trend</div>
          <div className="chart-card" style={{position:'relative'}}>
            <div className="chart-card-header">
              <div><div className="chart-card-title">Revenue (bars) vs GP% (line) — Aug 2025 to Jul 2026</div><div className="chart-card-sub">OMR thousands — primary board-level performance view</div></div>
              <div className="legend-row">
                <div className="legend-item"><div className="legend-dot" style={{background:'#1A56DB'}}></div>Revenue (OMR K)</div>
                <div className="legend-item"><div className="legend-dot" style={{background:'#10B981',borderRadius:'50%'}}></div>GP% (right axis)</div>
              </div>
            </div>
            <div style={{position:'relative'}}>
              <canvas id="mgmtTrendChart" height="80"></canvas>
            </div>
          </div>

          <div className="section-label">Segment Performance Scorecard</div>
          <div className="grid-3-2">
            <div className="chart-card">
              <div className="chart-card-title" style={{marginBottom:12}}>All Segments — July 2026</div>
              <table className="scorecard">
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
                  <tr><td><span className="badge muted">CCL</span></td><td>3</td><td>OMR 6K</td><td style={{color:'var(--red)',fontWeight:600}}>7%</td><td>3.4</td><td style={{color:'var(--muted)'}}>→ 0%</td></tr>
                  <tr><td><strong>Total</strong></td><td><strong>342</strong></td><td><strong>OMR 2.84M</strong></td><td style={{color:'var(--green)',fontWeight:700}}>25.7%</td><td><strong>8.9</strong></td><td className="t-up"><strong>↑+14%</strong></td></tr>
                </tbody>
              </table>
            </div>
            <div style={{display:'flex',flexDirection:'column',gap:12}}>
              <div className="chart-card" style={{flex:1, position:'relative'}}>
                <div className="chart-card-title" style={{marginBottom:10}}>Volume Mix by Segment</div>
                <div style={{position:'relative'}}><canvas id="volMixChart" height="140"></canvas></div>
              </div>
              <div className="chart-card" style={{flex:1, position:'relative'}}>
                <div className="chart-card-title" style={{marginBottom:10}}>Import vs Export Revenue — 6 Months</div>
                <div style={{position:'relative'}}><canvas id="impExpBar" height="110"></canvas></div>
              </div>
            </div>
          </div>

          <div className="section-label">Management Decisions — This Week</div>
          <div className="grid-2">
            <div className="action-item" style={{borderLeft:'3px solid var(--blue)'}}><div className="action-num" style={{background:'var(--blue)'}}>1</div><div><div className="action-title">Air freight growing 20%+ — expand or add partner?</div><div className="action-meta">AIR-IMP and AIR-EXP are highest GP% segments. Volume tests ceiling of current Emirates SkyCargo agreement. Renegotiate rates or add second airline partner.</div></div></div>
            <div className="action-item" style={{borderLeft:'3px solid var(--red)'}}><div className="action-num red">2</div><div><div className="action-title">LCL segments declining — review pricing or bundle?</div><div className="action-meta">LCL-IMP and LCL-EXP both down 3–5% with GP% near threshold. Consider bundling LCL as upsell for FCL customers rather than standalone product.</div></div></div>
            <div className="action-item" style={{borderLeft:'3px solid var(--amber-md)'}}><div className="action-num amber">3</div><div><div className="action-title">Falcon Imports at 8% GP — rate revision needed</div><div className="action-meta">Customs rejection costing OMR 42K in delays and penalties. Review whether contract rates cover actual costs. Initiate rate revision conversation.</div></div></div>
            <div className="action-item" style={{borderLeft:'3px solid var(--green)'}}><div className="action-num green">4</div><div><div className="action-title">July target within reach — prioritise invoicing now</div><div className="action-meta">OMR 360K needed in 2 days to hit OMR 3.2M target. 8 uninvoiced delivered jobs = OMR 286K ready to invoice immediately. Finance to act today.</div></div></div>
          </div>
        </div>

        <div className="sidebar">
          <div className="sidebar-card">
            <div className="sidebar-title">YTD Performance</div>
            <div className="metric-row"><span className="metric-label">YTD Revenue</span><span className="metric-val" style={{color:'var(--blue)'}}>OMR 18.4M</span></div>
            <div className="metric-row"><span className="metric-label">YTD Target</span><span className="metric-val">OMR 19.2M</span></div>
            <div className="metric-row"><span className="metric-label">YTD GP%</span><span className="metric-val" style={{color:'var(--green)'}}>24.1%</span></div>
            <div className="metric-row"><span className="metric-label">Total Jobs YTD</span><span className="metric-val">2,184</span></div>
            <div className="metric-row"><span className="metric-label">Avg Rev / Job</span><span className="metric-val">OMR 8,426</span></div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">Operational KPIs</div>
            <div style={{textAlign:'center',padding:'6px 0 10px'}}>
              <div style={{fontSize:30,fontWeight:700,fontFamily:"'JetBrains Mono',monospace",color:'var(--green)'}}>87%</div>
              <div style={{fontSize:11,color:'var(--muted)'}}>On-time delivery rate</div>
              <div className="prog-bar" style={{margin:'8px 0'}}><div className="prog-fill green" style={{width:'87%'}}></div></div>
              <div style={{fontSize:11,color:'var(--red)',fontWeight:600}}>▼ 3pp below 90% target</div>
            </div>
            <div style={{borderTop:'1px solid var(--border)', margin:'14px 0'}}></div>
            <div className="metric-row"><span className="metric-label">Avg Customs Days</span><span className="metric-val">3.2 days</span></div>
            <div className="metric-row"><span className="metric-label">Avg Job Duration</span><span className="metric-val">8.9 days</span></div>
            <div className="metric-row"><span className="metric-label">Quote Conversion</span><span className="metric-val" style={{color:'var(--green)'}}>68%</span></div>
          </div>
          <div className="sidebar-card">
            <div className="sidebar-title">Top Lanes — MTD</div>
            <div className="metric-row"><span className="metric-label" style={{fontSize:11}}>JBALI → Hamburg</span><span className="metric-val" style={{fontSize:11}}>42 jobs</span></div>
            <div className="metric-row"><span className="metric-label" style={{fontSize:11}}>Shanghai → DXB</span><span className="metric-val" style={{fontSize:11}}>38 jobs</span></div>
            <div className="metric-row"><span className="metric-label" style={{fontSize:11}}>DXB → JFK</span><span className="metric-val" style={{fontSize:11}}>29 jobs</span></div>
            <div className="metric-row"><span className="metric-label" style={{fontSize:11}}>Rotterdam → JBALI</span><span className="metric-val" style={{fontSize:11}}>24 jobs</span></div>
            <div className="metric-row"><span className="metric-label" style={{fontSize:11}}>Mumbai → DXB</span><span className="metric-val" style={{fontSize:11}}>21 jobs</span></div>
          </div>
        </div>
      </div>
    </>
  );
}
