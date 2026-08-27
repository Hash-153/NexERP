import React, { useState } from 'react';
import { Users, TrendingUp, DollarSign, Award, BarChart3, CheckCircle2 } from 'lucide-react';

export const CompensationEquityPage: React.FC = () => {
  const mockBands = [
    { grade: 'ENG-E3', title: 'Senior Software Engineer', min: 110000, mid: 135000, max: 160000, eeCount: 14, avgCompa: 98.2, payEquityGap: 0.8 },
    { grade: 'ENG-E4', title: 'Staff Systems Architect', min: 145000, mid: 175000, max: 210000, eeCount: 6, avgCompa: 101.5, payEquityGap: 0.4 },
    { grade: 'OPS-M2', title: 'Plant Production Manager', min: 95000, mid: 120000, max: 145000, eeCount: 5, avgCompa: 96.8, payEquityGap: 1.2 },
    { grade: 'FIN-A3', title: 'Senior Financial Analyst', min: 85000, mid: 105000, max: 125000, eeCount: 8, avgCompa: 102.1, payEquityGap: 0.6 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Compensation Bands & Pay Equity Analytics</h1>
          <p className="text-sm text-slate-500">Compa-Ratio grading distributions, market salary band penetration, and demographic pay equity compliance.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Average Org Compa-Ratio</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">99.4%</p>
          <span className="text-xs text-emerald-600 font-medium">Market Competitive (95-105%)</span>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Unadjusted Pay Equity Gap</span>
          <p className="text-2xl font-bold text-emerald-600 mt-1">&lt; 1.0%</p>
          <span className="text-xs text-slate-500">Statistically Insignificant</span>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Active Salary Bands</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">12 Grades</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Annual Merit Pool</span>
          <p className="text-2xl font-bold text-indigo-600 mt-1">3.5%</p>
          <span className="text-xs text-slate-500">Budget Allocated</span>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-600" /> Salary Grade Structures & Compa-Ratio Metrics
          </h3>
        </div>

        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700 text-slate-500 text-xs uppercase tracking-wider">
              <th className="p-4">Grade Code</th>
              <th className="p-4">Benchmark Position</th>
              <th className="p-4 text-right">Band Min</th>
              <th className="p-4 text-right">Midpoint</th>
              <th className="p-4 text-right">Band Max</th>
              <th className="p-4 text-center">FTEs</th>
              <th className="p-4 text-right">Avg Compa-Ratio</th>
              <th className="p-4 text-center">Pay Equity Gap</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {mockBands.map((b) => (
              <tr key={b.grade} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                <td className="p-4 font-mono font-bold text-slate-900 dark:text-white">{b.grade}</td>
                <td className="p-4 font-medium text-slate-900 dark:text-white">{b.title}</td>
                <td className="p-4 text-right font-mono text-slate-600 dark:text-slate-400">${b.min.toLocaleString()}</td>
                <td className="p-4 text-right font-mono font-semibold text-indigo-600">${b.mid.toLocaleString()}</td>
                <td className="p-4 text-right font-mono text-slate-600 dark:text-slate-400">${b.max.toLocaleString()}</td>
                <td className="p-4 text-center font-bold text-slate-700 dark:text-slate-300">{b.eeCount}</td>
                <td className="p-4 text-right font-mono font-bold text-slate-900 dark:text-white">{b.avgCompa}%</td>
                <td className="p-4 text-center">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300">
                    <CheckCircle2 className="w-3.5 h-3.5" /> {b.payEquityGap}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
