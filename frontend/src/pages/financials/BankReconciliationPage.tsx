import React, { useState } from 'react';
import { Landmark, ArrowRightLeft, Check, AlertCircle, Upload, CheckCircle2 } from 'lucide-react';

export const BankReconciliationPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'MATCHED' | 'UNMATCHED'>('MATCHED');

  const mockMatched = [
    { date: '2026-01-10', ref: 'CUST-WIRE-8891', stmtAmt: 5000.0, glAmt: 5000.0, status: 'EXACT_MATCH', partner: 'Quantum Dynamics Ltd' },
    { date: '2026-01-14', ref: 'ACH-DEPOSIT-4421', stmtAmt: 12450.0, glAmt: 12450.0, status: 'EXACT_MATCH', partner: 'Starlight Medical' },
    { date: '2026-01-20', ref: 'VEND-CHECK-1002', stmtAmt: -3200.0, glAmt: -3200.0, status: 'EXACT_MATCH', partner: 'Apex Fasteners Inc' },
  ];

  const mockUnmatched = [
    { date: '2026-01-28', ref: 'WIRE-FEE-INTL', stmtAmt: -45.0, type: 'BANK_SERVICE_FEE', suggestedAction: 'Auto-Post Bank Charge' },
    { date: '2026-01-30', ref: 'UNIDENTIFIED-CR-99', stmtAmt: 850.0, type: 'UNKNOWN_DEPOSIT', suggestedAction: 'Assign to Suspense Clearing' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Bank Statement Reconciliation (BRS)</h1>
          <p className="text-sm text-slate-500">Automated MT940 / BAI2 statement clearing against General Ledger cash accounts.</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium transition">
            <Upload className="w-4 h-4" /> Import Statement
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition">
            <CheckCircle2 className="w-4 h-4" /> Post Reconciled BRS
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Bank Statement Balance</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">$142,500.00</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">GL Book Balance</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">$141,695.00</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Reconciled Match Rate</span>
          <p className="text-xl font-bold text-emerald-600 mt-1">98.5%</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Unreconciled Variance</span>
          <p className="text-xl font-bold text-amber-600 mt-1">$805.00</p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('MATCHED')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${activeTab === 'MATCHED' ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'}`}
            >
              Matched Transactions ({mockMatched.length})
            </button>
            <button
              onClick={() => setActiveTab('UNMATCHED')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${activeTab === 'UNMATCHED' ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'}`}
            >
              Unmatched Exceptions ({mockUnmatched.length})
            </button>
          </div>
        </div>

        {activeTab === 'MATCHED' ? (
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4">Date</th>
                <th className="p-4">Reference</th>
                <th className="p-4">Counterparty</th>
                <th className="p-4 text-right">Statement Amount</th>
                <th className="p-4 text-right">GL Amount</th>
                <th className="p-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {mockMatched.map((m, i) => (
                <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                  <td className="p-4 text-slate-600 dark:text-slate-400">{m.date}</td>
                  <td className="p-4 font-mono font-medium text-slate-900 dark:text-white">{m.ref}</td>
                  <td className="p-4 text-slate-700 dark:text-slate-300">{m.partner}</td>
                  <td className="p-4 text-right font-mono font-semibold text-slate-900 dark:text-white">${m.stmtAmt.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-right font-mono font-semibold text-slate-900 dark:text-white">${m.glAmt.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-center">
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                      <Check className="w-3 h-3" /> Matched
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4">Date</th>
                <th className="p-4">Reference</th>
                <th className="p-4">Exception Type</th>
                <th className="p-4 text-right">Amount</th>
                <th className="p-4">Suggested Action</th>
                <th className="p-4 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
              {mockUnmatched.map((u, i) => (
                <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                  <td className="p-4 text-slate-600 dark:text-slate-400">{u.date}</td>
                  <td className="p-4 font-mono font-medium text-slate-900 dark:text-white">{u.ref}</td>
                  <td className="p-4 text-amber-600 font-medium">{u.type}</td>
                  <td className="p-4 text-right font-mono font-bold text-slate-900 dark:text-white">${u.stmtAmt.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                  <td className="p-4 text-slate-600 dark:text-slate-400 text-xs">{u.suggestedAction}</td>
                  <td className="p-4 text-center">
                    <button className="px-3 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 rounded text-xs font-semibold">
                      Resolve
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
