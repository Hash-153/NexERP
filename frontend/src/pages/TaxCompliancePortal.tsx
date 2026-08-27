import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface TaxNexusRecord {
  id: string;
  state: string;
  nexus_type: string;
  gross_sales: number;
  transactions_count: number;
  is_registered: boolean;
  collected_tax_ytd: number;
}

export function TaxCompliancePortal() {
  const kpis: KPICardData[] = [
    { title: 'Sales Tax Collected (YTD)', value: '$1,450,200', change: '+14.2%', isPositive: true, icon: '🏛️', subtitle: 'Remitted across 45 states' },
    { title: 'Active Economic Nexus States', value: '38 States', change: 'Wayfair Compliant', isPositive: true, icon: '📍', subtitle: '$100k+ sales threshold passed' },
    { title: 'Exemption Certificates Active', value: '284 Resellers', change: '100% Verified', isPositive: true, icon: '📜', subtitle: '501(c)(3) & Resale W-9s' },
    { title: 'Automated Tax Audit Score', value: 'Zero Penalties', change: 'Clean', isPositive: true, icon: '🛡️', subtitle: 'Precision zip+4 rate tables' },
  ];

  const nexus: TaxNexusRecord[] = [
    { id: '1', state: 'California (CA)', nexus_type: 'ECONOMIC_THRESHOLD_WAYFAIR', gross_sales: 8450000, transactions_count: 1420, is_registered: true, collected_tax_ytd: 612625 },
    { id: '2', state: 'Texas (TX)', nexus_type: 'PHYSICAL_PRESENCE_HQ', gross_sales: 12100000, transactions_count: 2840, is_registered: true, collected_tax_ytd: 756250 },
    { id: '3', state: 'New York (NY)', nexus_type: 'ECONOMIC_THRESHOLD_WAYFAIR', gross_sales: 3200000, transactions_count: 850, is_registered: true, collected_tax_ytd: 284000 },
    { id: '4', state: 'Washington (WA)', nexus_type: 'ECONOMIC_THRESHOLD_WAYFAIR', gross_sales: 2100000, transactions_count: 420, is_registered: true, collected_tax_ytd: 212100 },
  ];

  const columns: ColumnDef<TaxNexusRecord>[] = [
    { key: 'state', header: 'State / Jurisdiction', width: '25%', render: t => <span className="font-bold text-slate-900 dark:text-white">{t.state}</span> },
    { key: 'nexus_type', header: 'Nexus Basis', width: '25%', render: t => <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-800 font-mono">{t.nexus_type}</span> },
    { key: 'gross_sales', header: 'Gross Sales YTD', width: '18%', align: 'right', render: t => `$${t.gross_sales.toLocaleString()}` },
    { key: 'transactions_count', header: 'Orders', width: '12%', align: 'center' },
    { key: 'collected_tax_ytd', header: 'Tax Remitted', width: '20%', align: 'right', render: t => <span className="font-bold text-emerald-600 dark:text-emerald-400">${t.collected_tax_ytd.toLocaleString()}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Multi-State Tax Compliance &amp; Nexus Portal</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Wayfair economic nexus thresholds, precision zip+4 rate tables, and automated resale exemption certificates</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ➕ Upload Exemption Certificate
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Multi-State Tax Nexus Monitoring &amp; Filing Schedule"
        subtitle="Automatic tracking of revenue and transaction counts against statutory state Wayfair thresholds"
        columns={columns}
        data={nexus}
      />
    </div>
  );
}
