import React, { useState } from 'react';
import { AdvancedDataGrid, ColumnDef } from '../components/enterprise/AdvancedDataGrid';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

interface BudgetPlanRecord {
  id: string;
  plan_name: string;
  fiscal_year: number;
  version_type: string;
  revenue_budget: number;
  opex_budget: number;
  net_ebitda: number;
  ebitda_margin: number;
  status: string;
}

export function StrategicBudgeting() {
  const kpis: KPICardData[] = [
    { title: 'Approved Revenue Budget (FY26)', value: '$64,500,000', change: '+15.8%', isPositive: true, icon: '🎯', subtitle: 'Annual strategic target' },
    { title: 'OPEX Budget Allocation', value: '$46,200,000', change: 'Controlled', isPositive: true, icon: '📉', subtitle: 'Zero-based departmental caps' },
    { title: 'Target EBITDA Budget', value: '$18,300,000', change: '+22.4%', isPositive: true, icon: '📈', subtitle: '28.4% Operating margin' },
    { title: 'YTD Budget Variance', value: '+1.4% Favorable', change: 'Green', isPositive: true, icon: '🛡️', subtitle: 'Actuals vs plan pacing' },
  ];

  const plans: BudgetPlanRecord[] = [
    { id: '1', plan_name: 'FY2026 Board Approved Corporate Operating Plan', fiscal_year: 2026, version_type: 'ORIGINAL_APPROVED', revenue_budget: 64500000, opex_budget: 46200000, net_ebitda: 18300000, ebitda_margin: 28.4, status: 'BOARD_APPROVED' },
    { id: '2', plan_name: 'FY2026 Mid-Year Strategic Revision (R1)', fiscal_year: 2026, version_type: 'MID_YEAR_REVISED', revenue_budget: 68200000, opex_budget: 48100000, net_ebitda: 20100000, ebitda_margin: 29.5, status: 'DRAFT_PREPARATION' },
    { id: '3', plan_name: 'FY2026 Downside Economic Stress Test', fiscal_year: 2026, version_type: 'WORST_CASE_DOWNTURN', revenue_budget: 52000000, opex_budget: 41000000, net_ebitda: 11000000, ebitda_margin: 21.2, status: 'LOCKED_FROZEN' },
  ];

  const columns: ColumnDef<BudgetPlanRecord>[] = [
    { key: 'plan_name', header: 'Plan Description', width: '32%', render: p => <span className="font-bold text-slate-900 dark:text-white">{p.plan_name}</span> },
    { key: 'fiscal_year', header: 'FY', width: '8%', align: 'center', render: p => `FY${p.fiscal_year}` },
    { key: 'version_type', header: 'Version Type', width: '18%', render: p => <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-800 font-mono">{p.version_type}</span> },
    { key: 'revenue_budget', header: 'Revenue Target', width: '14%', align: 'right', render: p => `$${p.revenue_budget.toLocaleString()}` },
    { key: 'opex_budget', header: 'OPEX Budget', width: '14%', align: 'right', render: p => `$${p.opex_budget.toLocaleString()}` },
    { key: 'net_ebitda', header: 'EBITDA Target', width: '14%', align: 'right', render: p => <span className="font-bold text-emerald-600 dark:text-emerald-400">${p.net_ebitda.toLocaleString()} ({p.ebitda_margin}%)</span> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Budgeting & Strategic Planning</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Zero-based cost center allocations, 18-month rolling forecasts, and CAPEX DCF/NPV evaluation models</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
            ➕ New Budget Version
          </button>
          <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-semibold transition-colors">
            📊 CAPEX ROI Evaluator
          </button>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <AdvancedDataGrid
        title="Annual Corporate Strategic Plans"
        subtitle="Multi-entity revenue targets, OPEX department headcount limits, and EBITDA projections"
        columns={columns}
        data={plans}
      />
    </div>
  );
}
