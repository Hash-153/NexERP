import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface RMARecord {
  id: string;
  rma_number: string;
  customer_name: string;
  order_number: string;
  item_name: string;
  qty: number;
  reason: string;
  status: string;
}

export function CustomerSelfServicePortal() {
  const kpis: KPICardData[] = [
    { title: 'Open Self-Service RMAs', value: '12 Returns', change: 'Processed', isPositive: true, icon: '🔄', subtitle: 'Prepaid return shipping labels' },
    { title: 'Average RMA Resolution', value: '2.1 Days', change: '-18h', isPositive: true, icon: '⏱️', subtitle: 'Inspection to credit memo' },
    { title: 'Customer Return Rate', value: '1.2%', change: '-0.3%', isPositive: true, icon: '📦', subtitle: 'Quality-driven order volume' },
    { title: 'Instant Statement Downloads', value: '184 YTD', change: '+24%', isPositive: true, icon: '📄', subtitle: 'Self-service account reconciliation' },
  ];

  const rmas: RMARecord[] = [
    { id: '1', rma_number: 'RMA-2026-441', customer_name: 'Apex Precision Tools', order_number: 'SO-10928', item_name: 'High Torque Stepper Motor 48V', qty: 2, reason: 'DEFECTIVE_WARRANTY', status: 'AUTHORIZED_LABEL_ISSUED' },
    { id: '2', rma_number: 'RMA-2026-442', customer_name: 'BioHealth Labs', order_number: 'SO-10931', item_name: 'Optical Sensor Calibration Unit', qty: 1, reason: 'BUYERS_REMORSE', status: 'CREDIT_MEMO_ISSUED' },
    { id: '3', rma_number: 'RMA-2026-443', customer_name: 'Titan Heavy Machinery', order_number: 'SO-10940', item_name: 'Hydraulic Cylinder Seal Kit', qty: 5, reason: 'WRONG_ITEM_SHIPPED', status: 'PACKAGE_RECEIVED_INSPECTION' },
  ];

  const columns: ColumnDef<RMARecord>[] = [
    { key: 'rma_number', header: 'RMA #', width: '18%', render: r => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{r.rma_number}</span> },
    { key: 'customer_name', header: 'Customer', width: '22%' },
    { key: 'order_number', header: 'Original Order', width: '15%', render: r => <span className="font-mono">{r.order_number}</span> },
    { key: 'item_name', header: 'Item / Part', width: '22%' },
    { key: 'reason', header: 'Return Reason', width: '15%', render: r => <span className="text-xs font-mono">{r.reason}</span> },
    { key: 'status', header: 'Status', width: '15%', render: r => <span className={`px-2 py-0.5 rounded text-xs font-bold ${r.status === 'CREDIT_MEMO_ISSUED' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}`}>{r.status}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Customer Self-Service Portal</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Customer self-service order tracking, automated Return Merchandise Authorization (RMA), and PDF statements</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ➕ Request RMA Return
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Return Merchandise Authorizations (RMA)"
        subtitle="Automated warranty claims, return label generation, and restocking fee calculations"
        columns={columns}
        data={rmas}
      />
    </div>
  );
}
