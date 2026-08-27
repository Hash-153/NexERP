import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface AssetRecord {
  id: string;
  asset_tag: string;
  name: string;
  category: string;
  acquisition_cost: number;
  net_book_value: number;
  status: string;
  location: string;
}

export function FixedAssetsManagement() {
  const kpis: KPICardData[] = [
    { title: 'Gross Capitalized Assets', value: '$8,450,000', change: '+4.2%', isPositive: true, icon: '🏗️', subtitle: 'Total acquisition basis' },
    { title: 'Current Net Book Value (NBV)', value: '$6,250,000', change: '-1.8%', isPositive: false, icon: '📊', subtitle: 'Carrying amount after depreciation' },
    { title: 'Monthly Depreciation Run', value: '$124,500', change: 'On Track', isPositive: true, icon: '⏱️', subtitle: 'Straight-line & MACRS schedules' },
    { title: 'Physical Audit Compliance', value: '99.4%', change: '+0.6%', isPositive: true, icon: '🏷️', subtitle: 'Barcode/RFID verified tag scans' },
  ];

  const assets: AssetRecord[] = [
    { id: '1', asset_tag: 'FA-2026-001', name: 'CNC High Precision Milling Machine', category: 'MACHINERY_EQUIPMENT', acquisition_cost: 450000, net_book_value: 395000, status: 'ACTIVE_IN_SERVICE', location: 'Austin Plant - Bay 3' },
    { id: '2', asset_tag: 'FA-2026-002', name: 'Automated Guided Vehicle (AGV) Fleet', category: 'VEHICLES', acquisition_cost: 280000, net_book_value: 240000, status: 'ACTIVE_IN_SERVICE', location: 'Dallas Distribution Center' },
    { id: '3', asset_tag: 'FA-2026-003', name: 'Enterprise Server SAN Storage Cluster', category: 'IT_HARDWARE', acquisition_cost: 160000, net_book_value: 110000, status: 'ACTIVE_IN_SERVICE', location: 'HQ Datacenter Room 102' },
    { id: '4', asset_tag: 'FA-2026-004', name: 'Solar Array 250kW Rooftop Installation', category: 'BUILDINGS_PROPERTY', acquisition_cost: 650000, net_book_value: 610000, status: 'ACTIVE_IN_SERVICE', location: 'Austin Manufacturing Facility' },
  ];

  const columns: ColumnDef<AssetRecord>[] = [
    { key: 'asset_tag', header: 'Asset Tag', width: '15%', render: a => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{a.asset_tag}</span> },
    { key: 'name', header: 'Asset Description', width: '25%' },
    { key: 'category', header: 'Category', width: '18%', render: a => <span className="px-2 py-0.5 text-xs rounded bg-slate-100 dark:bg-slate-800">{a.category}</span> },
    { key: 'location', header: 'Facility / Location', width: '20%' },
    { key: 'acquisition_cost', header: 'Cost Basis', width: '11%', align: 'right', render: a => `$${a.acquisition_cost.toLocaleString()}` },
    { key: 'net_book_value', header: 'Net Book Value', width: '11%', align: 'right', render: a => <span className="font-bold text-slate-900 dark:text-white">${a.net_book_value.toLocaleString()}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Fixed Assets Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Multi-book depreciation engine, CIP project capitalization, and IAS 36 impairment testing</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
            ▶ Run Monthly Depreciation
          </button>
          <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-semibold transition-colors">
            ➕ Register Capital Asset
          </button>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Capitalized Fixed Assets Register"
        subtitle="Audit-compliant tracking of property, plant, machinery, IT, and software intangibles"
        columns={columns}
        data={assets}
      />
    </div>
  );
}
