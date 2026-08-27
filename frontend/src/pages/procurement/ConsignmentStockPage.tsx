import React, { useState } from 'react';
import { Plus, Building2, ArrowRightLeft, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

interface ConsignmentStock {
  id: string;
  vendor_id: string;
  vendor_name: string;
  item_code: string;
  item_description: string;
  location: string;
  on_hand_qty: number;
  consumed_qty: number;
  reported_qty: number;
  unit_cost: number;
  total_value: number;
  last_reconciled: string;
  status: 'reconciled' | 'pending' | 'discrepancy';
}

const MOCK_CONSIGNMENT: ConsignmentStock[] = [
  {
    id: 'CS-001',
    vendor_id: 'V-1001',
    vendor_name: 'Alpha Components Ltd',
    item_code: 'RAW-A100',
    item_description: 'Aluminum Alloy Rod 6061-T6',
    location: 'WH-A Zone 3',
    on_hand_qty: 850,
    consumed_qty: 120,
    reported_qty: 120,
    unit_cost: 4.25,
    total_value: 3612.50,
    last_reconciled: '2026-08-20',
    status: 'reconciled'
  },
  {
    id: 'CS-002',
    vendor_id: 'V-1002',
    vendor_name: 'Beta Chemicals Corp',
    item_code: 'CHEM-B220',
    item_description: 'Solvent Grade Ethanol 99.9%',
    location: 'WH-B Hazmat Bay',
    on_hand_qty: 200,
    consumed_qty: 48,
    reported_qty: 45,
    unit_cost: 12.80,
    total_value: 2560.00,
    last_reconciled: '2026-08-18',
    status: 'discrepancy'
  },
  {
    id: 'CS-003',
    vendor_id: 'V-1003',
    vendor_name: 'Omega Electronics',
    item_code: 'ELEC-C330',
    item_description: 'SMD Capacitor 100uF 50V',
    location: 'WH-C Electronics Shelf',
    on_hand_qty: 12000,
    consumed_qty: 3500,
    reported_qty: 0,
    unit_cost: 0.08,
    total_value: 960.00,
    last_reconciled: '2026-07-31',
    status: 'pending'
  }
];

const statusColor: Record<ConsignmentStock['status'], string> = {
  reconciled: 'bg-emerald-100 text-emerald-700',
  pending: 'bg-yellow-100 text-yellow-700',
  discrepancy: 'bg-red-100 text-red-700',
};

const statusIcon: Record<ConsignmentStock['status'], React.ReactNode> = {
  reconciled: <CheckCircle size={14} />,
  pending: <AlertTriangle size={14} />,
  discrepancy: <AlertTriangle size={14} />,
};

export default function ConsignmentStockPage() {
  const [stocks, setStocks] = useState<ConsignmentStock[]>(MOCK_CONSIGNMENT);
  const [filter, setFilter] = useState<'all' | ConsignmentStock['status']>('all');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [reconQty, setReconQty] = useState<string>('');

  const filtered = filter === 'all' ? stocks : stocks.filter(s => s.status === filter);
  const selected = stocks.find(s => s.id === selectedId);

  const totalValue = stocks.reduce((sum, s) => sum + s.total_value, 0);
  const discrepancies = stocks.filter(s => s.status === 'discrepancy').length;
  const pending = stocks.filter(s => s.status === 'pending').length;

  function handleReconcile() {
    if (!selectedId || !reconQty) return;
    const qty = parseFloat(reconQty);
    setStocks(prev => prev.map(s => {
      if (s.id !== selectedId) return s;
      const hasDiscrepancy = Math.abs(qty - s.consumed_qty) > 0.01;
      return {
        ...s,
        reported_qty: qty,
        status: hasDiscrepancy ? 'discrepancy' : 'reconciled',
        last_reconciled: new Date().toISOString().split('T')[0],
      };
    }));
    setSelectedId(null);
    setReconQty('');
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Building2 className="text-indigo-600" />
            Consignment Inventory Management
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Vendor-owned stock held at your warehouse — consumption triggers AP liability recognition.
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium">
          <Plus size={16} /> Add Agreement
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <p className="text-sm text-gray-500">Total Consignment Value</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-400 mt-1">{stocks.length} vendor agreements</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <p className="text-sm text-gray-500">Discrepancies</p>
          <p className={`text-2xl font-bold mt-1 ${discrepancies > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
            {discrepancies}
          </p>
          <p className="text-xs text-gray-400 mt-1">Variance between ERP vs vendor count</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <p className="text-sm text-gray-500">Pending Reconciliation</p>
          <p className={`text-2xl font-bold mt-1 ${pending > 0 ? 'text-yellow-600' : 'text-emerald-600'}`}>
            {pending}
          </p>
          <p className="text-xs text-gray-400 mt-1">Awaiting vendor confirmation</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(['all', 'reconciled', 'pending', 'discrepancy'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border ${
              filter === f
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Stock Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Agreement', 'Vendor', 'Item', 'On Hand', 'Consumed', 'Reported', 'Unit Cost', 'Value', 'Status', 'Actions'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {filtered.map(s => (
              <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 font-mono text-indigo-600 font-medium">{s.id}</td>
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-900">{s.vendor_name}</p>
                  <p className="text-xs text-gray-400">{s.location}</p>
                </td>
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-800">{s.item_code}</p>
                  <p className="text-xs text-gray-400 truncate max-w-[200px]">{s.item_description}</p>
                </td>
                <td className="px-4 py-3 text-right font-mono">{s.on_hand_qty.toLocaleString()}</td>
                <td className="px-4 py-3 text-right font-mono">{s.consumed_qty.toLocaleString()}</td>
                <td className="px-4 py-3 text-right font-mono">
                  <span className={s.reported_qty === 0 ? 'text-gray-400 italic' : ''}>
                    {s.reported_qty === 0 ? 'Not reported' : s.reported_qty.toLocaleString()}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-mono">${s.unit_cost.toFixed(2)}</td>
                <td className="px-4 py-3 text-right font-mono font-semibold">
                  ${s.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${statusColor[s.status]}`}>
                    {statusIcon[s.status]}
                    {s.status.charAt(0).toUpperCase() + s.status.slice(1)}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => { setSelectedId(s.id); setReconQty(s.consumed_qty.toString()); }}
                    className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    <ArrowRightLeft size={12} /> Reconcile
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Reconcile Modal */}
      {selectedId && selected && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-bold text-gray-900 mb-1">Vendor Reconciliation — {selectedId}</h2>
            <p className="text-sm text-gray-500 mb-4">{selected.vendor_name} · {selected.item_description}</p>

            <div className="space-y-3 text-sm mb-5">
              <div className="flex justify-between">
                <span className="text-gray-500">ERP Consumed Qty</span>
                <span className="font-semibold">{selected.consumed_qty.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Vendor Reported Qty</span>
                <input
                  type="number"
                  value={reconQty}
                  onChange={e => setReconQty(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 w-32 text-right font-mono focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              {reconQty && Math.abs(parseFloat(reconQty) - selected.consumed_qty) > 0.01 && (
                <div className="bg-red-50 border border-red-200 rounded p-2 text-red-700 text-xs">
                  ⚠ Variance: {(parseFloat(reconQty) - selected.consumed_qty).toFixed(0)} units — will flag as discrepancy.
                </div>
              )}
            </div>

            <div className="flex gap-3 justify-end">
              <button onClick={() => setSelectedId(null)} className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">
                Cancel
              </button>
              <button onClick={handleReconcile} className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">
                Confirm Reconciliation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
