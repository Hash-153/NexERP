import React, { useState } from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface ContractRecord {
  id: string;
  contract_number: string;
  title: string;
  counterparty_name: string;
  contract_type: string;
  total_value: number;
  effective_date: string;
  expiration_date: string;
  status: string;
}

export function ContractLifecycle() {
  const [activeTab, setActiveTab] = useState<'ACTIVE' | 'AUTHORING' | 'RENEWALS' | 'CLAUSES'>('ACTIVE');

  const kpis: KPICardData[] = [
    { title: 'Total Active Contract Value (ACV)', value: '$24,850,000', change: '+14.2%', isPositive: true, icon: '📜', subtitle: 'Across 142 enterprise contracts' },
    { title: 'Upcoming 60-Day Renewals', value: '$3,800,000', change: '18 Contracts', isPositive: true, icon: '🔄', subtitle: 'Auto-evergreen & CPI escalations' },
    { title: 'Milestone Billing Due (30D)', value: '$1,450,000', change: '8 Milestones', isPositive: true, icon: '💰', subtitle: 'Deliverable sign-off pending' },
    { title: 'Average Signature Turnaround', value: '4.2 Days', change: '-1.5 Days', isPositive: true, icon: '✍️', subtitle: 'Digital envelope execution' },
  ];

  const contracts: ContractRecord[] = [
    { id: '1', contract_number: 'MSA-2026-081', title: 'Global Enterprise SaaS & Managed Services Agreement', counterparty_name: 'Apex Dynamics International', contract_type: 'MASTER_SERVICES_AGREEMENT', total_value: 3600000, effective_date: '2026-01-01', expiration_date: '2028-12-31', status: 'ACTIVE_EXECUTED' },
    { id: '2', contract_number: 'SOW-2026-104', title: 'ERP Phase 2 MRP-II Implementation Statement of Work', counterparty_name: 'Titan Manufacturing Systems', contract_type: 'STATEMENT_OF_WORK', total_value: 850000, effective_date: '2026-02-15', expiration_date: '2026-11-30', status: 'ACTIVE_EXECUTED' },
    { id: '3', contract_number: 'VSC-2026-019', title: 'Strategic Raw Material Titanium Alloy Supply Agreement', counterparty_name: 'Vanguard Metallurgical Corp', contract_type: 'VENDOR_SUPPLY_CONTRACT', total_value: 5200000, effective_date: '2025-06-01', expiration_date: '2027-05-31', status: 'ACTIVE_EXECUTED' },
    { id: '4', contract_number: 'SLA-2026-033', title: 'Tier-1 Mission Critical 99.99% Availability Service SLA', counterparty_name: 'BioHealth Laboratories Inc', contract_type: 'SOFTWARE_LICENSE_SLA', total_value: 1200000, effective_date: '2026-03-01', expiration_date: '2027-02-28', status: 'OUT_FOR_SIGNATURE' },
  ];

  const columns: ColumnDef<ContractRecord>[] = [
    { key: 'contract_number', header: 'Contract #', width: '18%', render: c => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{c.contract_number}</span> },
    { key: 'title', header: 'Contract Title', width: '28%' },
    { key: 'counterparty_name', header: 'Counterparty', width: '20%' },
    { key: 'total_value', header: 'Total Value', width: '14%', align: 'right', render: c => <span className="font-bold text-slate-900 dark:text-white">${c.total_value.toLocaleString()}</span> },
    { key: 'expiration_date', header: 'Expiration Date', width: '10%' },
    { key: 'status', header: 'Status', width: '10%', render: c => <span className={`px-2 py-0.5 rounded text-xs font-bold ${c.status === 'ACTIVE_EXECUTED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>{c.status}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Contract Lifecycle Management (CLM)</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Dynamic legal clause authoring, milestone billing triggers, and automated CPI index renewal schedules</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
            ➕ Author New Contract
          </button>
          <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-semibold transition-colors">
            📚 Clause Library
          </button>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Enterprise Legal Contract Repository"
        subtitle="Centralized repository with milestone revenue schedules and compliance obligation monitors"
        columns={columns}
        data={contracts}
      />
    </div>
  );
}
