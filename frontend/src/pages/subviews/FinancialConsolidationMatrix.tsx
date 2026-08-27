import React from 'react';

export function FinancialConsolidationMatrix() {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
      <h3 className="text-lg font-bold text-slate-900 dark:text-white">Multi-Entity Legal Consolidation &amp; Elimination Grid</h3>
      <p className="text-xs text-slate-500">Corporate parent entity roll-up with automatic intercompany transactions netting</p>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 font-bold text-xs uppercase text-slate-600 dark:text-slate-300">
              <th className="p-3">Financial Line</th>
              <th className="p-3 text-right">Apex HQ (USD)</th>
              <th className="p-3 text-right">UK Sub (GBP)</th>
              <th className="p-3 text-right">Germany Sub (EUR)</th>
              <th className="p-3 text-right text-rose-600">Eliminations</th>
              <th className="p-3 text-right text-emerald-600 font-black">Consolidated Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-xs">
            <tr>
              <td className="p-3 font-sans font-semibold">Total Revenue</td>
              <td className="p-3 text-right">$4,850,000</td>
              <td className="p-3 text-right">$1,250,000</td>
              <td className="p-3 text-right">$1,620,000</td>
              <td className="p-3 text-right text-rose-600">-$1,000,000</td>
              <td className="p-3 text-right font-bold text-emerald-600">$6,720,000</td>
            </tr>
            <tr>
              <td className="p-3 font-sans font-semibold">Cost of Goods Sold</td>
              <td className="p-3 text-right">-$850,000</td>
              <td className="p-3 text-right">-$320,000</td>
              <td className="p-3 text-right">-$760,000</td>
              <td className="p-3 text-right text-rose-600">+$800,000</td>
              <td className="p-3 text-right font-bold text-emerald-600">-$1,130,000</td>
            </tr>
            <tr className="bg-slate-50 dark:bg-slate-800/50 font-bold">
              <td className="p-3 font-sans">Gross Profit</td>
              <td className="p-3 text-right">$4,000,000</td>
              <td className="p-3 text-right">$930,000</td>
              <td className="p-3 text-right">$860,000</td>
              <td className="p-3 text-right text-rose-600">-$200,000</td>
              <td className="p-3 text-right text-emerald-600">$5,590,000</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
