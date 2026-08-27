import React, { useState } from 'react';
import { Network, Route, GitFork, Package, Search, CheckCircle2, ArrowRight } from 'lucide-react';

export const WavePickingGenealogyPage: React.FC = () => {
  const [selectedLot, setSelectedLot] = useState('LOT-2026-TITANIUM-001');

  const mockGenealogy = {
    lotNumber: 'LOT-2026-TITANIUM-001',
    itemSku: 'TITANIUM-BAR-25MM',
    rawMaterialGRN: 'GRN-2026-0012 (Supplier: Apex Precision Metals)',
    productionOrders: ['PROD-2026-0042', 'PROD-2026-0048'],
    finishedGoodsLots: ['LOT-FG-SHAFT-991', 'LOT-FG-SHAFT-992'],
    customerShipments: [
      { dlvNumber: 'DLV-2026-0014', customer: 'Quantum Aerospace Corp', qty: 150, date: '2026-02-15' },
      { dlvNumber: 'DLV-2026-0018', customer: 'Starlight Defense Systems', qty: 200, date: '2026-02-20' },
    ]
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Lot Genealogy & FDA 21 CFR Traceability Explorer</h1>
          <p className="text-sm text-slate-500">Bi-directional backward/forward lot pedigree tracing from raw material vendor heat lots to finished customer deliveries.</p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Network className="w-5 h-5 text-indigo-600" /> Bi-Directional Genealogy Tree: {selectedLot}
          </h3>
          <span className="px-3 py-1 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-mono text-xs font-bold rounded-full border border-indigo-200 dark:border-indigo-800">
            FDA 21 CFR Part 11 Compliant
          </span>
        </div>

        {/* Visual Lineage Nodes Flow */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
          {/* Step 1: Supplier Inbound */}
          <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">1. Inbound Supplier Lot</span>
            <p className="font-mono font-bold text-slate-900 dark:text-white text-xs">{mockGenealogy.lotNumber}</p>
            <p className="text-xs text-slate-600 dark:text-slate-400">{mockGenealogy.rawMaterialGRN}</p>
          </div>

          {/* Step 2: Shop Floor Conversion */}
          <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">2. Manufacturing Orders</span>
            <div className="flex flex-wrap gap-1">
              {mockGenealogy.productionOrders.map((po) => (
                <span key={po} className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 text-xs font-mono rounded">
                  {po}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-500">CNC Milling & Heat Treat</p>
          </div>

          {/* Step 3: Finished Goods Lot */}
          <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">3. Finished Goods Lots</span>
            <div className="flex flex-wrap gap-1">
              {mockGenealogy.finishedGoodsLots.map((fg) => (
                <span key={fg} className="px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 text-xs font-mono rounded font-bold">
                  {fg}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-500">Passed Final QC Inspection</p>
          </div>

          {/* Step 4: Customer Dispatches */}
          <div className="p-4 bg-slate-50 dark:bg-slate-900/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">4. Downstream Customer Deliveries</span>
            <p className="text-xs font-bold text-indigo-600">2 Customer Shipments Contained</p>
            <p className="text-xs text-slate-500">Total 350 Units in Market</p>
          </div>
        </div>

        {/* Customer Shipment Containment Table */}
        <div className="space-y-3 pt-2">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Traceable Customer Outbound Consignments</h4>
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-3">Dispatch Number</th>
                <th className="p-3">Customer Entity</th>
                <th className="p-3 text-right">Quantity Shipped</th>
                <th className="p-3 text-right">Dispatch Date</th>
                <th className="p-3 text-center">Recall Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700 text-xs">
              {mockGenealogy.customerShipments.map((s) => (
                <tr key={s.dlvNumber} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                  <td className="p-3 font-mono font-medium text-slate-900 dark:text-white">{s.dlvNumber}</td>
                  <td className="p-3 font-semibold text-slate-900 dark:text-white">{s.customer}</td>
                  <td className="p-3 text-right font-mono text-slate-900 dark:text-white">{s.qty} Units</td>
                  <td className="p-3 text-right font-mono text-slate-500">{s.date}</td>
                  <td className="p-3 text-center">
                    <span className="px-2.5 py-0.5 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-full text-xs font-semibold">
                      Traceable & Contained
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
