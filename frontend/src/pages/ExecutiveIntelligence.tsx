import React from 'react';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

export function ExecutiveIntelligence() {
  const kpis: KPICardData[] = [
    { title: 'Altman Z-Score Solvency', value: '4.85 (Safe)', change: '+0.42', isPositive: true, icon: '🛡️', subtitle: 'Bankruptcy distress distance' },
    { title: 'DuPont Return on Equity (ROE)', value: '24.8%', change: '+3.2%', isPositive: true, icon: '📈', subtitle: 'Margin x Turnover x Leverage' },
    { title: 'Cash Conversion Cycle (CCC)', value: '38 Days', change: '-6 Days', isPositive: true, icon: '⚡', subtitle: 'DSO + DIO - DPO efficiency' },
    { title: 'Enterprise Net Working Capital', value: '$8,450,000', change: '+9.4%', isPositive: true, icon: '💼', subtitle: 'Current Assets - Current Liab' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Executive Intelligence Cockpit</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">C-suite financial radar, DuPont 3-stage ROE decomposition, and Altman Z-score solvency analytics</p>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">DuPont 3-Stage ROE Decomposition</h3>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>Net Profit Margin (Net Income / Revenue)</span>
              <span className="font-bold font-mono text-blue-600 dark:text-blue-400">14.2%</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>Asset Turnover (Revenue / Total Assets)</span>
              <span className="font-bold font-mono text-blue-600 dark:text-blue-400">1.25x</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>Equity Multiplier (Total Assets / Equity)</span>
              <span className="font-bold font-mono text-blue-600 dark:text-blue-400">1.40x</span>
            </div>
            <div className="flex justify-between p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg font-bold">
              <span>Return on Equity (ROE = Margin x Turnover x Leverage)</span>
              <span className="text-emerald-700 dark:text-emerald-300 font-mono text-base">24.85%</span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Altman Z-Score Solvency Multipliers</h3>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>X1: Working Capital / Total Assets (1.2 Weight)</span>
              <span className="font-bold font-mono">0.68</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>X2: Retained Earnings / Total Assets (1.4 Weight)</span>
              <span className="font-bold font-mono">1.12</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>X3: EBIT / Total Assets (3.3 Weight)</span>
              <span className="font-bold font-mono">1.85</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
              <span>X4: Market Equity / Total Liabilities (0.6 Weight)</span>
              <span className="font-bold font-mono">1.20</span>
            </div>
            <div className="flex justify-between p-4 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-lg font-bold">
              <span>Composite Altman Z-Score (&gt; 2.99 = Safe Zone)</span>
              <span className="text-blue-700 dark:text-blue-300 font-mono text-base">4.85 (Ultra Safe)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
