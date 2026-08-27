import React, { useState } from 'react';

export function DataAnalyticsWorkbench() {
  const [selectedMetric, setSelectedMetric] = useState('REVENUE');

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">Enterprise Data Analytics &amp; OLAP Workbench</h3>
          <p className="text-xs text-slate-500">Ad-hoc multi-dimensional slice-and-dice cube for financial and operational metrics</p>
        </div>
        <select
          value={selectedMetric}
          onChange={e => setSelectedMetric(e.target.value)}
          className="px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-semibold"
        >
          <option value="REVENUE">Revenue &amp; Gross Margin</option>
          <option value="CASH_FLOW">Cash Conversion Cycle (CCC)</option>
          <option value="EBITDA">Operating EBITDA Pacing</option>
          <option value="OEE">Manufacturing OEE Efficiency</option>
        </select>
      </div>

      <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3">
        <div className="flex justify-between items-center text-sm font-bold text-slate-800 dark:text-slate-200">
          <span>Enterprise Dimension Hierarchy: Entity &gt; Region &gt; Cost Center &gt; Product Line</span>
          <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs">Run Query</button>
        </div>
        <div className="grid grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-3 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-700">
            <div className="text-slate-400">Total Sliced Value</div>
            <div className="text-base font-black text-slate-900 dark:text-white mt-1">$24,850,000</div>
          </div>
          <div className="p-3 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-700">
            <div className="text-slate-400">YoY Growth</div>
            <div className="text-base font-black text-emerald-600 mt-1">+18.4%</div>
          </div>
          <div className="p-3 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-700">
            <div className="text-slate-400">Variance to Budget</div>
            <div className="text-base font-black text-blue-600 mt-1">+2.1% Favorable</div>
          </div>
          <div className="p-3 bg-white dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-700">
            <div className="text-slate-400">Forecast Accuracy</div>
            <div className="text-base font-black text-slate-900 dark:text-white mt-1">98.2%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
