import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface ShipmentRecord {
  id: string;
  bol_number: string;
  carrier_name: string;
  origin: string;
  destination: string;
  chargeable_weight: number;
  total_cost: number;
  status: string;
}

export function LogisticsFleet() {
  const kpis: KPICardData[] = [
    { title: 'Active Dispatches in Transit', value: '48 Loads', change: '+6 Loads', isPositive: true, icon: '🚛', subtitle: 'FTL, LTL & Air freight' },
    { title: 'On-Time Delivery (OTD)', value: '97.8%', change: '+1.2%', isPositive: true, icon: '⏱️', subtitle: 'Carrier SLA benchmark' },
    { title: 'Average Freight Cost / kg', value: '$1.84', change: '-4.5%', isPositive: true, icon: '📉', subtitle: 'Dimensional weight optimized' },
    { title: 'Cold Chain Geofence Alerts', value: '0 Breaches', change: 'Clean', isPositive: true, icon: '❄️', subtitle: 'Live IoT telemetry verified' },
  ];

  const shipments: ShipmentRecord[] = [
    { id: '1', bol_number: 'BOL-2026-9812', carrier_name: 'FedEx Freight Priority', origin: 'Dallas, TX', destination: 'Chicago, IL', chargeable_weight: 4200, total_cost: 3850, status: 'IN_TRANSIT' },
    { id: '2', bol_number: 'BOL-2026-9813', carrier_name: 'Old Dominion Freight Line', origin: 'Atlanta, GA', destination: 'New York, NY', chargeable_weight: 1850, total_cost: 1420, status: 'OUT_FOR_DELIVERY' },
    { id: '3', bol_number: 'BOL-2026-9814', carrier_name: 'Maersk Ocean Logistics', origin: 'Rotterdam Port', destination: 'Houston, TX', chargeable_weight: 18500, total_cost: 9200, status: 'IN_TRANSIT' },
    { id: '4', bol_number: 'BOL-2026-9815', carrier_name: 'Estes Express Lines', origin: 'Los Angeles, CA', destination: 'Seattle, WA', chargeable_weight: 3100, total_cost: 2650, status: 'BOOKED' },
  ];

  const columns: ColumnDef<ShipmentRecord>[] = [
    { key: 'bol_number', header: 'BOL / Tracking Number', width: '22%', render: s => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{s.bol_number}</span> },
    { key: 'carrier_name', header: 'Carrier', width: '22%' },
    { key: 'origin', header: 'Origin', width: '15%' },
    { key: 'destination', header: 'Destination', width: '15%' },
    { key: 'chargeable_weight', header: 'Weight (kg)', width: '12%', align: 'right', render: s => `${s.chargeable_weight.toLocaleString()} kg` },
    { key: 'total_cost', header: 'Freight Cost', width: '14%', align: 'right', render: s => <span className="font-bold text-slate-900 dark:text-white">${s.total_cost.toLocaleString()}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Logistics & Fleet Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Carrier rate shopping, dynamic dimensional freight calculation, and GPS cold-chain telematics</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ➕ Book New Dispatch
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Live Consignment Shipments"
        subtitle="Multi-modal freight tracking with automated electronic Bill of Lading (BOL)"
        columns={columns}
        data={shipments}
      />
    </div>
  );
}
