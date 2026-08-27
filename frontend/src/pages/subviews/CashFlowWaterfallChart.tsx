import React from 'react';

export interface WaterfallStep {
  name: string;
  amount: number;
  type: 'START' | 'INFLOW' | 'OUTFLOW' | 'END';
}

interface CashFlowWaterfallChartProps {
  steps?: WaterfallStep[];
  currency?: string;
  title?: string;
}

export function CashFlowWaterfallChart({
  steps = [
    { name: 'Beginning Cash', amount: 8500000, type: 'START' },
    { name: 'AR Collections', amount: 4850000, type: 'INFLOW' },
    { name: 'Customer Subscriptions', amount: 1250000, type: 'INFLOW' },
    { name: 'Vendor AP Payments', amount: -2450000, type: 'OUTFLOW' },
    { name: 'Payroll & Benefits', amount: -1850000, type: 'OUTFLOW' },
    { name: 'Facility Leases', amount: -420000, type: 'OUTFLOW' },
    { name: 'CAPEX Investments', amount: -650000, type: 'OUTFLOW' },
    { name: 'Tax Provisions', amount: -380000, type: 'OUTFLOW' },
    { name: 'Ending Liquid Cash', amount: 9850000, type: 'END' },
  ],
  currency = 'USD',
  title = 'Monthly Cash Flow Inflow / Outflow Waterfall',
}: CashFlowWaterfallChartProps) {
  const maxVal = Math.max(...steps.map(s => Math.abs(s.amount))) * 1.25;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">{title}</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">Reconciliation of operating, investing, and financing liquid balances</p>
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500"></span> Inflow</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-rose-500"></span> Outflow</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-blue-600"></span> Balance</span>
        </div>
      </div>

      <div className="grid grid-cols-9 gap-3 h-64 items-end pb-8 pt-4 px-2 border-b border-slate-100 dark:border-slate-800">
        {steps.map((step, idx) => {
          const heightPct = Math.min(Math.round((Math.abs(step.amount) / maxVal) * 100), 100);
          const isPositive = step.amount >= 0;

          let colorClass = 'bg-blue-600';
          if (step.type === 'INFLOW') colorClass = 'bg-emerald-500';
          if (step.type === 'OUTFLOW') colorClass = 'bg-rose-500';

          return (
            <div key={idx} className="flex flex-col items-center h-full justify-end group relative">
              <div className="text-xs font-mono font-bold mb-2 text-slate-700 dark:text-slate-300">
                {isPositive ? '+' : '-'}${Math.abs(step.amount / 1000).toFixed(0)}k
              </div>
              <div
                className={`w-full rounded-t-lg transition-all duration-300 shadow-sm ${colorClass} hover:opacity-90`}
                style={{ height: `${heightPct}%` }}
              ></div>
              <div className="absolute -bottom-7 text-[11px] font-medium text-slate-500 dark:text-slate-400 text-center w-full truncate" title={step.name}>
                {step.name}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
