import React, { useState } from 'react';
import { Activity, TrendingUp, AlertTriangle, Calendar, BarChart3 } from 'lucide-react';

interface WorkCenter {
  id: string;
  name: string;
  capacity_hours_per_week: number;
}

interface MPS {
  item_code: string;
  description: string;
  planned_qty: number;
  due_week: string;
  routing_steps: RoutingStep[];
}

interface RoutingStep {
  work_center_id: string;
  hours_per_unit: number;
}

interface CapacityBucket {
  work_center_id: string;
  work_center_name: string;
  week: string;
  required_hours: number;
  available_hours: number;
  utilization_pct: number;
  is_overloaded: boolean;
}

const WORK_CENTERS: WorkCenter[] = [
  { id: 'WC-001', name: 'CNC Lathe', capacity_hours_per_week: 40 },
  { id: 'WC-002', name: 'Milling', capacity_hours_per_week: 35 },
  { id: 'WC-003', name: 'Assembly', capacity_hours_per_week: 60 },
  { id: 'WC-004', name: 'QC Inspection', capacity_hours_per_week: 20 },
];

const MPS_SAMPLE: MPS[] = [
  {
    item_code: 'FG-A001',
    description: 'Widget Pro Alpha',
    planned_qty: 200,
    due_week: '2026-W36',
    routing_steps: [
      { work_center_id: 'WC-001', hours_per_unit: 0.1 },
      { work_center_id: 'WC-002', hours_per_unit: 0.08 },
      { work_center_id: 'WC-003', hours_per_unit: 0.15 },
      { work_center_id: 'WC-004', hours_per_unit: 0.05 },
    ]
  },
  {
    item_code: 'FG-B002',
    description: 'Precision Bracket B',
    planned_qty: 500,
    due_week: '2026-W36',
    routing_steps: [
      { work_center_id: 'WC-001', hours_per_unit: 0.12 },
      { work_center_id: 'WC-002', hours_per_unit: 0.10 },
      { work_center_id: 'WC-003', hours_per_unit: 0.08 },
      { work_center_id: 'WC-004', hours_per_unit: 0.04 },
    ]
  },
  {
    item_code: 'FG-C003',
    description: 'Housing Assembly C',
    planned_qty: 150,
    due_week: '2026-W37',
    routing_steps: [
      { work_center_id: 'WC-001', hours_per_unit: 0.08 },
      { work_center_id: 'WC-002', hours_per_unit: 0.06 },
      { work_center_id: 'WC-003', hours_per_unit: 0.20 },
      { work_center_id: 'WC-004', hours_per_unit: 0.06 },
    ]
  }
];

function computeRCCP(mps: MPS[], workCenters: WorkCenter[]): CapacityBucket[] {
  const weekMap: Record<string, Record<string, number>> = {};

  for (const order of mps) {
    if (!weekMap[order.due_week]) weekMap[order.due_week] = {};
    for (const step of order.routing_steps) {
      const prev = weekMap[order.due_week][step.work_center_id] || 0;
      weekMap[order.due_week][step.work_center_id] = prev + step.hours_per_unit * order.planned_qty;
    }
  }

  const buckets: CapacityBucket[] = [];
  for (const [week, wcMap] of Object.entries(weekMap)) {
    for (const wc of workCenters) {
      const required = wcMap[wc.id] || 0;
      const utilization = (required / wc.capacity_hours_per_week) * 100;
      buckets.push({
        work_center_id: wc.id,
        work_center_name: wc.name,
        week,
        required_hours: required,
        available_hours: wc.capacity_hours_per_week,
        utilization_pct: utilization,
        is_overloaded: utilization > 100,
      });
    }
  }

  return buckets.sort((a, b) => a.week.localeCompare(b.week) || a.work_center_id.localeCompare(b.work_center_id));
}

export default function RCCPPage() {
  const [mpsOrders] = useState<MPS[]>(MPS_SAMPLE);
  const [workCenters] = useState<WorkCenter[]>(WORK_CENTERS);
  const buckets = computeRCCP(mpsOrders, workCenters);

  const overloaded = buckets.filter(b => b.is_overloaded);
  const weeks = [...new Set(buckets.map(b => b.week))].sort();

  function getUtilColor(pct: number) {
    if (pct > 100) return 'bg-red-500';
    if (pct > 85) return 'bg-yellow-400';
    return 'bg-emerald-500';
  }

  function getUtilText(pct: number) {
    if (pct > 100) return 'text-red-700 bg-red-50 border-red-200';
    if (pct > 85) return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    return 'text-emerald-700 bg-emerald-50 border-emerald-200';
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Activity className="text-purple-600" />
          Rough Cut Capacity Planning (RCCP)
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          High-level capacity feasibility check of MPS against work-center available hours. No finite scheduling constraints applied.
        </p>
      </div>

      {/* KPI Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">MPS Orders</p>
          <p className="text-2xl font-bold text-gray-900">{mpsOrders.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Work Centers</p>
          <p className="text-2xl font-bold text-gray-900">{workCenters.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Planning Weeks</p>
          <p className="text-2xl font-bold text-gray-900">{weeks.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p className="text-xs text-gray-500">Overloaded Buckets</p>
          <p className={`text-2xl font-bold ${overloaded.length > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
            {overloaded.length}
          </p>
        </div>
      </div>

      {/* Overload Alerts */}
      {overloaded.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="text-red-600" size={18} />
            <h3 className="font-semibold text-red-800">Capacity Overloads Detected</h3>
          </div>
          <div className="space-y-1">
            {overloaded.map(b => (
              <p key={`${b.week}-${b.work_center_id}`} className="text-sm text-red-700">
                Week <strong>{b.week}</strong> — {b.work_center_name}: {b.required_hours.toFixed(1)} hrs required vs {b.available_hours} hrs available ({b.utilization_pct.toFixed(0)}% utilization)
              </p>
            ))}
          </div>
        </div>
      )}

      {/* MPS Summary Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <Calendar size={16} className="text-purple-500" />
            Master Production Schedule
          </h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Item Code', 'Description', 'Planned Qty', 'Due Week', 'Routing Steps'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {mpsOrders.map(o => (
              <tr key={o.item_code} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-indigo-600 font-medium">{o.item_code}</td>
                <td className="px-4 py-3 text-gray-800">{o.description}</td>
                <td className="px-4 py-3 text-right font-semibold">{o.planned_qty.toLocaleString()}</td>
                <td className="px-4 py-3 font-mono">{o.due_week}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">{o.routing_steps.map(r => r.work_center_id).join(' → ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Capacity Loading Heat Grid */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <BarChart3 size={16} className="text-purple-500" />
            Capacity Load by Work Center & Week
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase sticky left-0 bg-gray-50">Work Center</th>
                {weeks.map(w => (
                  <th key={w} className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase">{w}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {workCenters.map(wc => (
                <tr key={wc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 sticky left-0 bg-white">
                    <p className="font-medium text-gray-900">{wc.name}</p>
                    <p className="text-xs text-gray-400">{wc.capacity_hours_per_week} hrs/week avail.</p>
                  </td>
                  {weeks.map(w => {
                    const bucket = buckets.find(b => b.week === w && b.work_center_id === wc.id);
                    if (!bucket || bucket.required_hours === 0) {
                      return (
                        <td key={w} className="px-4 py-4 text-center">
                          <span className="text-gray-300 text-xs">—</span>
                        </td>
                      );
                    }
                    return (
                      <td key={w} className="px-4 py-4 text-center">
                        <div className={`inline-flex flex-col items-center gap-1 px-3 py-2 rounded-lg border text-xs font-semibold ${getUtilText(bucket.utilization_pct)}`}>
                          <span>{bucket.utilization_pct.toFixed(0)}%</span>
                          <span className="font-normal">{bucket.required_hours.toFixed(1)} hrs</span>
                        </div>
                        {/* Mini progress bar */}
                        <div className="mt-1 h-1.5 w-20 mx-auto bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${getUtilColor(bucket.utilization_pct)}`}
                            style={{ width: `${Math.min(bucket.utilization_pct, 100)}%` }}
                          />
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
