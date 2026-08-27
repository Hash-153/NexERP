import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface SubRecord {
  id: string;
  customer_name: string;
  plan: string;
  arr: number;
  mrr: number;
  seats: number;
  deferred_rev: number;
  status: string;
}

export function SubscriptionBillingPortal() {
  const kpis: KPICardData[] = [
    { title: 'Annual Recurring Revenue (ARR)', value: '$18,450,000', change: '+24.5%', isPositive: true, icon: '🔁', subtitle: 'Net Revenue Retention: 128%' },
    { title: 'Monthly Recurring Revenue (MRR)', value: '$1,537,500', change: '+2.1%', isPositive: true, icon: '📈', subtitle: 'Contracted SaaS subscription base' },
    { title: 'ASC 606 Deferred Revenue Pool', value: '$8,250,000', change: 'Amortizing', isPositive: true, icon: '⏳', subtitle: 'Unearned subscription liability' },
    { title: 'Gross Logo Churn Rate', value: '1.4%', change: '-0.4%', isPositive: true, icon: '🛡️', subtitle: 'Top tier SaaS benchmark (<2%)' },
  ];

  const subs: SubRecord[] = [
    { id: '1', customer_name: 'Apex Dynamics International', plan: 'Enterprise Unlimited (Multi-Tenant)', arr: 960000, mrr: 80000, seats: 1200, deferred_rev: 720000, status: 'ACTIVE' },
    { id: '2', customer_name: 'Titan Heavy Machinery Corp', plan: 'Manufacturing Pro + Advanced WMS', arr: 480000, mrr: 40000, seats: 500, deferred_rev: 320000, status: 'ACTIVE' },
    { id: '3', customer_name: 'BioHealth Laboratories', plan: 'FDA 21 CFR Compliant LifeSciences Tier', arr: 650000, mrr: 54166, seats: 750, deferred_rev: 487500, status: 'ACTIVE' },
  ];

  const columns: ColumnDef<SubRecord>[] = [
    { key: 'customer_name', header: 'Customer Organization', width: '28%' },
    { key: 'plan', header: 'Subscription Tier Plan', width: '25%' },
    { key: 'seats', header: 'Active Seats', width: '12%', align: 'center', render: s => s.seats.toLocaleString() },
    { key: 'mrr', header: 'MRR', width: '12%', align: 'right', render: s => `$${s.mrr.toLocaleString()}` },
    { key: 'arr', header: 'ARR Target', width: '12%', align: 'right', render: s => <span className="font-bold text-slate-900 dark:text-white">${s.arr.toLocaleString()}</span> },
    { key: 'status', header: 'Status', width: '11%', render: s => <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800">{s.status}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Subscription Recurring Billing &amp; ASC 606</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Multi-tier SaaS recurring contracts, ASC 606 revenue recognition waterfalls, and automated renewal management</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ➕ New Subscription Contract
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Active Recurring SaaS Contracts"
        subtitle="Live ARR contracts with monthly revenue recognition amortization and unearned revenue balances"
        columns={columns}
        data={subs}
      />
    </div>
  );
}
