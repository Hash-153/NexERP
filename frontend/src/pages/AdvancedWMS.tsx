import React from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface WaveRecord {
  id: string;
  wave_number: string;
  priority: number;
  total_lines: number;
  picked_lines: number;
  status: string;
  cutoff: string;
}

export function AdvancedWMS() {
  const kpis: KPICardData[] = [
    { title: 'Active Pick Waves', value: '14 Waves', change: '840 Lines', isPositive: true, icon: '📦', subtitle: 'Assigned to RF gun pickers' },
    { title: 'Warehouse Bin Utilization', value: '88.6%', change: '+2.1%', isPositive: true, icon: '🏢', subtitle: 'Velocity-optimized slotting' },
    { title: 'Dock Turnaround Time', value: '42 Min', change: '-8 Min', isPositive: true, icon: '🚚', subtitle: 'Average dwell per trailer' },
    { title: 'Pick Accuracy Rate', value: '99.92%', change: '+0.04%', isPositive: true, icon: '🎯', subtitle: 'Barcode scan verified' },
  ];

  const waves: WaveRecord[] = [
    { id: '1', wave_number: 'WAVE-20260301-A1', priority: 1, total_lines: 120, picked_lines: 118, status: 'IN_PROGRESS', cutoff: '14:00 Today' },
    { id: '2', wave_number: 'WAVE-20260301-B2', priority: 2, total_lines: 95, picked_lines: 95, status: 'COMPLETED', cutoff: '16:30 Today' },
    { id: '3', wave_number: 'WAVE-20260301-C3', priority: 3, total_lines: 180, picked_lines: 45, status: 'RELEASED', cutoff: '18:00 Today' },
    { id: '4', wave_number: 'WAVE-20260301-D4', priority: 4, total_lines: 60, picked_lines: 0, status: 'RELEASED', cutoff: '20:00 Today' },
  ];

  const columns: ColumnDef<WaveRecord>[] = [
    { key: 'wave_number', header: 'Wave Number', width: '25%', render: w => <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{w.wave_number}</span> },
    { key: 'priority', header: 'Priority', width: '15%', align: 'center', render: w => <span className="px-2 py-0.5 rounded text-xs bg-amber-100 text-amber-800 font-bold">P{w.priority}</span> },
    { key: 'total_lines', header: 'Total Lines', width: '15%', align: 'center' },
    { key: 'picked_lines', header: 'Picked Lines', width: '15%', align: 'center', render: w => `${w.picked_lines} / ${w.total_lines} (${Math.round((w.picked_lines / w.total_lines) * 100)}%)` },
    { key: 'cutoff', header: 'Carrier Cutoff', width: '15%' },
    { key: 'status', header: 'Status', width: '15%', render: w => <span className={`px-2 py-0.5 rounded text-xs font-bold ${w.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}`}>{w.status}</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Advanced Warehouse Management (WMS)</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Velocity-based 3D slotting, directed wave/zone picking, and yard dock door appointment scheduling</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
            ⚡ Release New Wave
          </button>
          <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-semibold transition-colors">
            🧠 Optimize Bin Slotting
          </button>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Active Wave Picking Batches"
        subtitle="Synchronized order wave grouping by carrier dispatch cutoff deadlines"
        columns={columns}
        data={waves}
      />
    </div>
  );
}
