import React from 'react';
import { KanbanWorkflowBoard, KanbanColumn } from '../components/enterprise/KanbanWorkflowBoard';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

export function CRMLeadsPipeline() {
  const kpis: KPICardData[] = [
    { title: 'Total Weighted Pipeline', value: '$8,450,000', change: '+18.5%', isPositive: true, icon: '🎯', subtitle: 'Probability-weighted deals' },
    { title: 'Average Deal Size', value: '$145,000', change: '+6.2%', isPositive: true, icon: '💼', subtitle: 'Enterprise ERP subscriptions' },
    { title: 'Win Rate (CPQ Quotes)', value: '42.8%', change: '+4.1%', isPositive: true, icon: '🏆', subtitle: 'Proposal to closed won' },
    { title: 'Sales Cycle Velocity', value: '48 Days', change: '-7 Days', isPositive: true, icon: '⚡', subtitle: 'Lead creation to signature' },
  ];

  const columns: KanbanColumn[] = [
    {
      id: 'PROSPECTING',
      title: 'Prospecting & Scoring',
      color: 'bg-slate-400',
      cards: [
        { id: '1', title: 'Global Logistics Corp', subtitle: '1,200 users, SAP migration project', tag: 'Score: 92/100', score: 92, owner: 'Alex Rivera', date: 'Exp: 30d' },
        { id: '2', title: 'Apex Medical Devices', subtitle: 'FDA 21 CFR compliance requirement', tag: 'Score: 84/100', score: 84, owner: 'Sarah Chen', date: 'Exp: 45d' },
      ],
    },
    {
      id: 'NEEDS_ANALYSIS',
      title: 'Solution Architecture',
      color: 'bg-blue-500',
      cards: [
        { id: '3', title: 'Titan Heavy Machinery', subtitle: 'MRP-II & Shop floor automation', tag: '$480,000', score: 88, owner: 'Marcus Vance', date: 'Exp: 60d' },
      ],
    },
    {
      id: 'PROPOSAL_CPQ',
      title: 'CPQ Quote Presented',
      color: 'bg-amber-500',
      cards: [
        { id: '4', title: 'Vanguard Aerospace Parts', subtitle: 'Multi-site AS9100 quality control', tag: '$650,000', score: 95, owner: 'Alex Rivera', date: 'Exp: 15d' },
      ],
    },
    {
      id: 'CLOSED_WON',
      title: 'Closed & Contracted',
      color: 'bg-emerald-500',
      cards: [
        { id: '5', title: 'Horizon Energy Systems', subtitle: 'Annual recurring contract signed', tag: '$920,000', score: 100, owner: 'Sarah Chen', date: 'Won Today' },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">CRM & Opportunity Pipeline</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Predictive lead scoring heuristics, CPQ quotation margin floors, and sales territory quotas</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
            ➕ Create Opportunity
          </button>
          <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-semibold transition-colors">
            📄 New CPQ Quote
          </button>
        </div>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <KanbanWorkflowBoard columns={columns} />
    </div>
  );
}
