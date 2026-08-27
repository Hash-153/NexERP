import React, { useState } from 'react';
import { Building2, Calculator, TrendingDown, DollarSign, Calendar, Plus, Check } from 'lucide-react';

export const FixedAssetRegisterPage: React.FC = () => {
  const [selectedAsset, setSelectedAsset] = useState<string>('FA-CNC-001');

  const mockAssets = [
    { id: 'FA-CNC-001', name: 'Haas VF-4 5-Axis CNC Mill', category: 'Machinery & Equipment', acqDate: '2024-01-15', cost: 125000.0, salvage: 15000.0, lifeYears: 5, method: 'STRAIGHT_LINE', bookVal: 81000.0, status: 'ACTIVE' },
    { id: 'FA-SRV-002', name: 'Enterprise Dell PowerEdge Cluster', category: 'IT Hardware', acqDate: '2025-03-01', cost: 45000.0, salvage: 5000.0, lifeYears: 3, method: 'DOUBLE_DECLINING_BALANCE', bookVal: 25000.0, status: 'ACTIVE' },
    { id: 'FA-FLT-003', name: 'Toyota 8FGU25 Forklift 5000lb', category: 'Vehicles & Fleet', acqDate: '2023-06-10', cost: 38000.0, salvage: 6000.0, lifeYears: 7, method: 'STRAIGHT_LINE', bookVal: 24285.0, status: 'ACTIVE' },
  ];

  const mockSchedule = [
    { year: 1, depExpense: 22000.0, monthlyDep: 1833.33, accumDep: 22000.0, endingBookVal: 103000.0, isPosted: true },
    { year: 2, depExpense: 22000.0, monthlyDep: 1833.33, accumDep: 44000.0, endingBookVal: 81000.0, isPosted: true },
    { year: 3, depExpense: 22000.0, monthlyDep: 1833.33, accumDep: 66000.0, endingBookVal: 59000.0, isPosted: false },
    { year: 4, depExpense: 22000.0, monthlyDep: 1833.33, accumDep: 88000.0, endingBookVal: 37000.0, isPosted: false },
    { year: 5, depExpense: 22000.0, monthlyDep: 1833.33, accumDep: 110000.0, endingBookVal: 15000.0, isPosted: false },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Fixed Asset Register & Depreciation Amortization</h1>
          <p className="text-sm text-slate-500">Capitalized Plant, Property & Equipment (PPE) register, SLN/DDB/SYD depreciation schedules, and monthly General Ledger accrual postings.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition shadow-sm">
          <Plus className="w-4 h-4" /> Capitalize New Asset
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Total Capitalized PPE Cost</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">$208,000.00</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Accumulated Depreciation</span>
          <p className="text-2xl font-bold text-amber-600 mt-1">($77,715.00)</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Net Book Value (NBV)</span>
          <p className="text-2xl font-bold text-emerald-600 mt-1">$130,285.00</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Active Asset Items</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">3 Units</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Asset List */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-4 space-y-3">
          <h3 className="font-semibold text-slate-900 dark:text-white text-sm">Capitalized PPE Assets</h3>
          <div className="space-y-2">
            {mockAssets.map((asset) => (
              <div
                key={asset.id}
                onClick={() => setSelectedAsset(asset.id)}
                className={`p-3 rounded-lg border cursor-pointer transition ${selectedAsset === asset.id ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20' : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-750'}`}
              >
                <div className="flex justify-between items-start">
                  <span className="font-semibold text-slate-900 dark:text-white text-sm">{asset.name}</span>
                  <span className="font-mono text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded text-slate-600 dark:text-slate-300">{asset.id}</span>
                </div>
                <div className="flex justify-between items-center text-xs text-slate-500 mt-2">
                  <span>{asset.category}</span>
                  <span className="font-mono font-bold text-slate-900 dark:text-white">${asset.cost.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Amortization Schedule Table */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
            <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <Calculator className="w-5 h-5 text-indigo-600" /> Multi-Year Amortization Schedule ({selectedAsset})
            </h3>
            <span className="text-xs px-2.5 py-1 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium rounded-full">
              Straight-Line Method (SLN)
            </span>
          </div>

          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4">Fiscal Year</th>
                <th className="p-4 text-right">Annual Expense</th>
                <th className="p-4 text-right">Monthly Accrual</th>
                <th className="p-4 text-right">Accumulated Depr</th>
                <th className="p-4 text-right">Ending Book Value</th>
                <th className="p-4 text-center">GL Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {mockSchedule.map((row) => (
                <tr key={row.year} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                  <td className="p-4 font-semibold text-slate-900 dark:text-white">Year {row.year}</td>
                  <td className="p-4 text-right font-mono font-medium text-slate-900 dark:text-white">${row.depExpense.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-right font-mono text-slate-600 dark:text-slate-400">${row.monthlyDep.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-right font-mono text-amber-600 font-semibold">${row.accumDep.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-right font-mono font-bold text-emerald-600">${row.endingBookVal.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-center">
                    {row.isPosted ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                        <Check className="w-3 h-3" /> Posted
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                        Scheduled
                      </span>
                    )}
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
