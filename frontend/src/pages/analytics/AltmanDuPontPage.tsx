import React from 'react';
import { TrendingUp, ShieldAlert, BarChart3, PieChart, Activity, CheckCircle2 } from 'lucide-react';

export const AltmanDuPontPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Executive Solvency & DuPont ROE Decomposition</h1>
          <p className="text-sm text-slate-500">Altman Z-Score financial distress forecasting and 5-stage DuPont Return on Equity driver analysis.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Altman Z-Score Card */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-xs text-slate-500 font-medium">Altman Z-Score (Manufacturing)</span>
              <p className="text-3xl font-black text-emerald-600 mt-1">4.35</p>
            </div>
            <span className="px-3 py-1 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 rounded-full text-xs font-bold">
              SAFE ZONE (&gt;2.99)
            </span>
          </div>

          <p className="text-xs text-slate-600 dark:text-slate-400">
            Probability of financial insolvency within 24 months is near zero. Robust balance sheet liquidity and retained earnings.
          </p>

          <div className="space-y-2 border-t border-slate-100 dark:border-slate-700 pt-3 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Working Capital / Assets (X1)</span>
              <span className="font-mono font-bold text-slate-900 dark:text-white">0.30</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Retained Earnings / Assets (X2)</span>
              <span className="font-mono font-bold text-slate-900 dark:text-white">0.40</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">EBIT / Assets (X3)</span>
              <span className="font-mono font-bold text-slate-900 dark:text-white">0.20</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Market Equity / Liabilities (X4)</span>
              <span className="font-mono font-bold text-slate-900 dark:text-white">2.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Asset Turnover (X5)</span>
              <span className="font-mono font-bold text-slate-900 dark:text-white">1.20x</span>
            </div>
          </div>
        </div>

        {/* DuPont 5-Stage Card */}
        <div className="md:col-span-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-xs text-slate-500 font-medium">Return on Equity (ROE) Decomposition</span>
              <p className="text-3xl font-black text-indigo-600 mt-1">40.0% ROE</p>
            </div>
            <span className="text-xs font-semibold text-slate-500">5-Stage DuPont Identity</span>
          </div>

          <div className="grid grid-cols-5 gap-2 text-center pt-2">
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-lg border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] text-slate-500 block">Tax Burden</span>
              <span className="text-sm font-bold font-mono text-slate-900 dark:text-white mt-1 block">0.79x</span>
            </div>
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-lg border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] text-slate-500 block">Interest Burden</span>
              <span className="text-sm font-bold font-mono text-slate-900 dark:text-white mt-1 block">0.95x</span>
            </div>
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-lg border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] text-slate-500 block">Operating Margin</span>
              <span className="text-sm font-bold font-mono text-indigo-600 mt-1 block">13.3%</span>
            </div>
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-lg border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] text-slate-500 block">Asset Turnover</span>
              <span className="text-sm font-bold font-mono text-slate-900 dark:text-white mt-1 block">2.00x</span>
            </div>
            <div className="p-2.5 bg-slate-50 dark:bg-slate-900/60 rounded-lg border border-slate-200 dark:border-slate-800">
              <span className="text-[11px] text-slate-500 block">Equity Multiplier</span>
              <span className="text-sm font-bold font-mono text-emerald-600 mt-1 block">2.00x</span>
            </div>
          </div>

          <div className="p-4 bg-indigo-50/50 dark:bg-indigo-950/20 rounded-lg border border-indigo-100 dark:border-indigo-900/40 text-xs text-slate-700 dark:text-slate-300">
            <span className="font-semibold text-indigo-900 dark:text-indigo-200 block mb-1">Key Performance Driver:</span>
            High return on equity is primarily driven by efficient capital utilization (2.0x Asset Turnover) and strong operating margin (13.3%), rather than excessive financial leverage.
          </div>
        </div>
      </div>
    </div>
  );
};
