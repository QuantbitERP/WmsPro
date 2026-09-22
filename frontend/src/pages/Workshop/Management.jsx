import React, { useState, useEffect } from 'react';
import Chart from 'chart.js/auto';
import { 
  DollarSign, TrendingUp, AlertCircle, FileText, CheckCircle2, 
  Download, ArrowUpRight, BarChart3, PieChart, Layers, Clock, ShieldCheck
} from 'lucide-react';

export default function WorkshopManagement() {
  const [billingFilter, setBillingFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // KPIs based on Workshop Summary DocType
  const kpis = [
    { label: 'Total Workshop Cost (MTD)', value: 'OMR 84,250', sub: '↑ 8% vs last month', trend: 'up', type: 'info', icon: '💰' },
    { label: 'Parts Consumption', value: 'OMR 51,400', sub: '61% of total expenditure', trend: 'up', type: 'warning', icon: '📦' },
    { label: 'Labour Billed', value: 'OMR 32,850', sub: '542 billable hours logged', trend: 'up', type: 'success', icon: '⏱️' },
    { label: 'Avg Cost Variance', value: '+3.4%', sub: 'Within 10% tolerance limit', trend: 'down', type: 'info', icon: '📊' },
    { label: 'Avg Turnaround (TAT)', value: '1.9 Days', sub: '↓ 0.4 days improvement', trend: 'up', type: 'success', icon: '⚡' },
  ];

  const summaries = [
    {
      id: 'WS-2026-0031',
      date: '2026-09-20',
      vehicle: 'VH-0104 (Volvo FH16)',
      jobCard: 'JC-2026-0042',
      labourCost: 'OMR 1,850',
      partsCost: 'OMR 4,200',
      grandTotal: 'OMR 6,050',
      estCost: 'OMR 5,800',
      variance: '+4.3%',
      billingType: 'Internal Fleet Cost',
      posting: 'JV-2026-0188',
      qcStatus: 'Passed',
      qcDoc: 'VRC-2026-0031'
    },
    {
      id: 'WS-2026-0030',
      date: '2026-09-19',
      vehicle: 'VH-0089 (Tata Prima)',
      jobCard: 'JC-2026-0039',
      labourCost: 'OMR 1,200',
      partsCost: 'OMR 3,150',
      grandTotal: 'OMR 4,350',
      estCost: 'OMR 4,400',
      variance: '-1.1%',
      billingType: 'Customer',
      posting: 'SINV-2026-0512',
      qcStatus: 'Passed',
      qcDoc: 'VRC-2026-0030'
    },
    {
      id: 'WS-2026-0029',
      date: '2026-09-18',
      vehicle: 'VH-0211 (BharatBenz)',
      jobCard: 'JC-2026-0037',
      labourCost: 'OMR 980',
      partsCost: 'OMR 1,520',
      grandTotal: 'OMR 2,500',
      estCost: 'OMR 2,200',
      variance: '+13.6%',
      billingType: 'Insurance Company',
      posting: 'SINV-2026-0508',
      qcStatus: 'Passed',
      qcDoc: 'VRC-2026-0029'
    },
    {
      id: 'WS-2026-0028',
      date: '2026-09-17',
      vehicle: 'VH-0340 (Eicher Pro)',
      jobCard: 'JC-2026-0033',
      labourCost: 'OMR 650',
      partsCost: 'OMR 1,890',
      grandTotal: 'OMR 2,540',
      estCost: 'OMR 2,600',
      variance: '-2.3%',
      billingType: 'Warranty Repair',
      posting: 'JV-2026-0179',
      qcStatus: 'Passed',
      qcDoc: 'VRC-2026-0028'
    },
    {
      id: 'WS-2026-0027',
      date: '2026-09-16',
      vehicle: 'VH-0199 (Ashok Leyland)',
      jobCard: 'JC-2026-0031',
      labourCost: 'OMR 1,420',
      partsCost: 'OMR 2,840',
      grandTotal: 'OMR 4,260',
      estCost: 'OMR 4,100',
      variance: '+3.9%',
      billingType: 'Internal Fleet Cost',
      posting: 'JV-2026-0174',
      qcStatus: 'Passed',
      qcDoc: 'VRC-2026-0027'
    },
    {
      id: 'WS-2026-0026',
      date: '2026-09-15',
      vehicle: 'VH-0182 (Tata Prima)',
      jobCard: 'JC-2026-0028',
      labourCost: 'OMR 2,100',
      partsCost: 'OMR 5,600',
      grandTotal: 'OMR 7,700',
      estCost: 'OMR 7,500',
      variance: '+2.6%',
      billingType: 'Customer',
      posting: 'SINV-2026-0498',
      qcStatus: 'Passed',
      qcDoc: 'VRC-2026-0026'
    }
  ];

  useEffect(() => {
    // Chart 1: Monthly Cost Composition
    const ctx1 = document.getElementById('monthlyCostChart');
    if (ctx1) {
      const existing1 = Chart.getChart('monthlyCostChart');
      if (existing1) existing1.destroy();

      new Chart('monthlyCostChart', {
        type: 'bar',
        data: {
          labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep (MTD)'],
          datasets: [
            {
              label: 'Spare Parts (OMR)',
              data: [38000, 42000, 49000, 46000, 52000, 51400],
              backgroundColor: '#1A56DB',
              borderRadius: 4
            },
            {
              label: 'In-House Labour (OMR)',
              data: [22000, 25000, 28000, 29000, 31000, 32850],
              backgroundColor: '#10B981',
              borderRadius: 4
            },
            {
              label: 'External Vendor Repairs (OMR)',
              data: [6000, 8000, 7500, 9500, 7000, 8500],
              backgroundColor: '#F59E0B',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { stacked: true, grid: { display: false } },
            y: { 
              stacked: true, 
              grid: { color: '#E2E8F0' },
              ticks: { callback: (v) => 'OMR ' + (v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v) }
            }
          },
          plugins: {
            legend: {
              position: 'top',
              labels: { boxWidth: 10, font: { size: 12, family: "'Inter', sans-serif" } }
            }
          }
        }
      });
    }

    // Chart 2: Billing Type Share
    const ctx2 = document.getElementById('billingShareChart');
    if (ctx2) {
      const existing2 = Chart.getChart('billingShareChart');
      if (existing2) existing2.destroy();

      new Chart('billingShareChart', {
        type: 'pie',
        data: {
          labels: ['Internal Fleet Cost', 'Customer Billing', 'Insurance Claims', 'Warranty Recovery'],
          datasets: [{
            data: [52, 28, 14, 6],
            backgroundColor: ['#1A56DB', '#10B981', '#F59E0B', '#8B5CF6'],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { boxWidth: 10, padding: 8, font: { size: 11 } }
            }
          }
        }
      });
    }
  }, []);

  const filteredSummaries = summaries.filter(s => {
    const matchesBilling = billingFilter === 'All' || s.billingType === billingFilter;
    const matchesSearch = s.vehicle.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          s.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          s.jobCard.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesBilling && matchesSearch;
  });

  return (
    <div className="main-layout" style={{ flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div className="page-header" style={{ marginBottom: '0' }}>
        <div>
          <h1>Workshop Analytics & Financial Summary</h1>
          <p>Expenditure audit, parts vs. labour margins, insurance recovery, and ERP financial postings</p>
        </div>
        <div className="header-right">
          <span className="period-pill">FY 2026-27 · MTD</span>
          <button 
            className="topbar-btn" 
            style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}
            onClick={() => alert('Exporting Workshop Financial Summary as CSV')}
          >
            <Download size={14} /> Export Summary
          </button>
        </div>
      </div>

      {/* Top Financial Counters - Row-Wise */}
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

      {/* Charts Row - Side-by-Side (Row-Wise) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px', width: '100%' }}>
        {/* Left: Monthly Trend */}
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Workshop Expenditure Breakdown</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Monthly comparison of Spare Parts, In-House Labour, and External Vendor Work</p>
            </div>
          </div>
          <div style={{ height: '260px', position: 'relative' }}>
            <canvas id="monthlyCostChart"></canvas>
          </div>
        </div>

        {/* Right: Billing Type Distribution */}
        <div className="chart-card" style={{ background: '#fff', padding: '18px 20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--ink)' }}>Cost Recovery & Billing Channels</h3>
              <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Breakdown by Settlement & Invoice channel</p>
            </div>
          </div>
          <div style={{ height: '260px', position: 'relative' }}>
            <canvas id="billingShareChart"></canvas>
          </div>
        </div>
      </div>

      {/* Workshop Summary & Financial Postings Table */}
      <div className="tbl-card" style={{ background: '#fff', padding: '20px', borderRadius: 'var(--radius)', border: '1px solid var(--border)', boxShadow: 'var(--shadow)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: '700', color: 'var(--ink)' }}>Submitted Workshop Summaries & Postings</h3>
            <p style={{ fontSize: '12px', color: 'var(--muted)' }}>Completed vehicle work orders with auto-generated Journal Entries and Invoices</p>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <input 
              type="text" 
              placeholder="Search Vehicle or JC..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                padding: '6px 12px',
                borderRadius: '20px',
                border: '1px solid var(--border)',
                fontSize: '12.5px',
                width: '190px'
              }}
            />
            <select 
              className="filter-select"
              value={billingFilter}
              onChange={(e) => setBillingFilter(e.target.value)}
              style={{ padding: '6px 28px 6px 12px', fontSize: '12.5px' }}
            >
              <option value="All">All Billing Types</option>
              <option value="Internal Fleet Cost">Internal Fleet Cost</option>
              <option value="Customer">Customer</option>
              <option value="Insurance Company">Insurance Company</option>
              <option value="Warranty Repair">Warranty Repair</option>
            </select>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)', color: 'var(--muted)', fontWeight: '600', textTransform: 'uppercase', fontSize: '12px', background: 'var(--surface)' }}>
                <th style={{ padding: '10px 12px' }}>Summary ID</th>
                <th style={{ padding: '10px 12px' }}>Vehicle</th>
                <th style={{ padding: '10px 12px' }}>Job Card</th>
                <th style={{ padding: '10px 12px' }}>Labour Cost</th>
                <th style={{ padding: '10px 12px' }}>Parts Cost</th>
                <th style={{ padding: '10px 12px' }}>Grand Total</th>
                <th style={{ padding: '10px 12px' }}>Est. Variance</th>
                <th style={{ padding: '10px 12px' }}>Billing Type</th>
                <th style={{ padding: '10px 12px' }}>ERP Posting</th>
                <th style={{ padding: '10px 12px' }}>QC Release</th>
              </tr>
            </thead>
            <tbody>
              {filteredSummaries.map((row, idx) => (
                <tr 
                  key={idx} 
                  style={{ 
                    borderBottom: '1px solid var(--border)',
                    backgroundColor: idx % 2 === 0 ? '#fff' : 'var(--surface)'
                  }}
                >
                  <td style={{ padding: '10px 12px', fontWeight: '600', color: 'var(--blue)' }}>{row.id}</td>
                  <td style={{ padding: '10px 12px', fontWeight: '600', color: 'var(--ink)' }}>{row.vehicle}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--ink-2)' }}>{row.jobCard}</td>
                  <td style={{ padding: '10px 12px', fontFamily: "'JetBrains Mono', monospace" }}>{row.labourCost}</td>
                  <td style={{ padding: '10px 12px', fontFamily: "'JetBrains Mono', monospace" }}>{row.partsCost}</td>
                  <td style={{ padding: '10px 12px', fontWeight: '700', color: 'var(--ink)', fontFamily: "'JetBrains Mono', monospace" }}>{row.grandTotal}</td>
                  <td style={{ padding: '10px 12px' }}>
                    <span 
                      style={{ 
                        fontWeight: '600',
                        color: row.variance.startsWith('-') ? 'var(--green)' : parseFloat(row.variance) > 10 ? 'var(--red)' : 'var(--amber)' 
                      }}
                    >
                      {row.variance}
                    </span>
                  </td>
                  <td style={{ padding: '10px 12px' }}>
                    <span 
                      style={{
                        padding: '3px 9px',
                        borderRadius: '12px',
                        fontSize: '11.5px',
                        fontWeight: '600',
                        backgroundColor: row.billingType === 'Customer' ? '#E6F7F2' : 
                                         row.billingType === 'Insurance Company' ? '#FEF3C7' :
                                         row.billingType === 'Warranty Repair' ? '#F5F3FF' : '#EBF2FF',
                        color: row.billingType === 'Customer' ? '#0A7A55' : 
                               row.billingType === 'Insurance Company' ? '#B45309' :
                               row.billingType === 'Warranty Repair' ? '#7C3AED' : '#1A56DB'
                      }}
                    >
                      {row.billingType}
                    </span>
                  </td>
                  <td style={{ padding: '10px 12px', fontFamily: "'JetBrains Mono', monospace", fontWeight: '600', color: 'var(--ink-3)' }}>
                    {row.posting}
                  </td>
                  <td style={{ padding: '10px 12px' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--green)', fontWeight: '600', fontSize: '12px' }}>
                      <CheckCircle2 size={14} /> {row.qcStatus}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
