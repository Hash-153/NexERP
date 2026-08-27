import React, { useState } from 'react';
import { DollarSign, RefreshCw, ArrowUpRight, ArrowDownRight, Globe, CheckCircle2 } from 'lucide-react';

export const CurrencyRevaluationPage: React.FC = () => {
  const [selectedCurrency, setSelectedCurrency] = useState('EUR');
  const [closingRate, setClosingRate] = useState('1.1000');
  const [isCalculated, setIsCalculated] = useState(false);

  const mockAccounts = [
    { code: '10150', name: 'Euro Operating Bank Account', curr: 'EUR', foreignBal: 100000.0, bookValUSD: 105000.0, revaluedUSD: 110000.0, gainLoss: 5000.0, isGain: true },
    { code: '20150', name: 'Euro Vendor Trade Payables', curr: 'EUR', foreignBal: 40000.0, bookValUSD: 42000.0, revaluedUSD: 44000.0, gainLoss: -2000.0, isGain: false },
    { code: '10160', name: 'GBP Barclays Treasury Account', curr: 'GBP', foreignBal: 75000.0, bookValUSD: 95250.0, revaluedUSD: 96000.0, gainLoss: 750.0, isGain: true },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Multi-Currency FX Revaluation (ASC 830 / IAS 21)</h1>
          <p className="text-sm text-slate-500">Revalue foreign currency denominated monetary balances and generate month-end unrealized gain/loss vouchers.</p>
        </div>
        <button
          onClick={() => setIsCalculated(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition"
        >
          <RefreshCw className="w-4 h-4" /> Run FX Revaluation
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Functional Currency</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">USD ($)</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Revaluation Date</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">2026-01-31</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Net Unrealized Gain</span>
          <p className="text-xl font-bold text-emerald-600 mt-1">+$3,750.00</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Target GL Account</span>
          <p className="text-xl font-bold text-slate-900 dark:text-white mt-1">40900 (FX Gain/Loss)</p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Globe className="w-5 h-5 text-indigo-600" /> Foreign Monetary Balances Register
          </h3>
          <span className="text-xs px-2.5 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-full font-medium">
            3 Reconcilable Accounts
          </span>
        </div>
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
              <th className="p-4">Account Code</th>
              <th className="p-4">Account Name</th>
              <th className="p-4">Currency</th>
              <th className="p-4 text-right">Foreign Balance</th>
              <th className="p-4 text-right">Historical Book (USD)</th>
              <th className="p-4 text-right">Revalued Book (USD)</th>
              <th className="p-4 text-right">Unrealized Gain / (Loss)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {mockAccounts.map((acc, idx) => (
              <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                <td className="p-4 font-mono font-medium text-slate-900 dark:text-white">{acc.code}</td>
                <td className="p-4 text-slate-700 dark:text-slate-300">{acc.name}</td>
                <td className="p-4 font-semibold text-indigo-600">{acc.curr}</td>
                <td className="p-4 text-right font-mono text-slate-900 dark:text-white">{acc.foreignBal.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                <td className="p-4 text-right font-mono text-slate-600 dark:text-slate-400">${acc.bookValUSD.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                <td className="p-4 text-right font-mono font-semibold text-slate-900 dark:text-white">${acc.revaluedUSD.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                <td className={`p-4 text-right font-mono font-bold ${acc.isGain ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {acc.isGain ? `+$${acc.gainLoss.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : `-$${Math.abs(acc.gainLoss).toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
