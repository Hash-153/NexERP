import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface WorkOrderRecord {
  id: string;
  order_number: string;
  customer_name: string;
  site_address: string;
  technician_name: string;
  sla_tier: string;
  status: string;
}

export function FieldServiceOperations() {
  const kpis: KPICardData[] = [
    { title: 'Open Field Work Orders', value: '28 Orders', change: '+3 Today', isPositive: true, icon: '🔧', subtitle: 'Dispatched to field teams' },
    { title: 'First-Time Fix Rate', value: '92.4%', change: '+3.1%', isPositive: true, icon: '🎯', subtitle: 'Resolved on initial visit' },
    { title: 'Average Response Time', value: '1.8 Hours', change: '-25 Min', isPositive: true, icon: '⏱️', subtitle: 'Critical P1 emergency SLA' },
    { title: 'Customer CSAT Score', value: '4.88 / 5', change: '+0.12', isPositive: true, icon: '⭐', subtitle: 'Post-service signature rating' },
  ];

  const workOrders: WorkOrderRecord[] = [
    { id: '1', order_number: 'FSO-20260301-101', customer_name: 'Apex Precision Tools', site_address: '100 Industrial Parkway, Austin TX', technician_name: 'Carlos Mendez (HVAC Master)', sla_tier: 'P1_FOUR_HOUR', status: 'ON_SITE' },
    { id: '2', order_number: 'FSO-20260301-102', customer_name: 'BioHealth Labs', site_address: '45 Science Center Dr, San Diego CA', technician_name: 'Emily Watson (PLC Specialist)', sla_tier: 'P2_NEXT_DAY', status: 'DISPATCHED' },
    { id: '3', order_number: 'FSO-20260301-103', customer_name: 'Metro Food Processing', site_address: '780 Logistics Blvd, Chicago IL', technician_name: 'David Kim (Senior Mech)', sla_tier: 'P2_NEXT_DAY', status: 'COMPLETED' },
  ];

  const columns: ColumnDef<WorkOrderRecord>[] = [
    { key: 'order_number', header: 'Work Order #', width: '20%', render: w => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{w.order_number}</span> },
    { key: 'customer_name', header: 'Customer', width: '22%' },
    { key: 'site_address', header: 'Site Location', width: '24%' },
    { key: 'technician_name', header: 'Assigned Engineer', width: '20%' },
    { key: 'status', header: 'Status', width: '14%', render: w => <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-100 text-blue-800">{w.status}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Field Service Operations</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Skill-based technician dispatch scheduling, van stock parts debiting, and digital sign-off</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ➕ Dispatch Field Engineer
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Field Service Dispatch Schedule"
        subtitle="Live tracking of technician assignments, travel geofencing, and work order progress"
        columns={columns}
        data={workOrders}
      />
    </div>
  );
}
