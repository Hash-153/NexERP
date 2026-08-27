import React from 'react';
import { GanttTimelineChart, GanttTask } from '../components/enterprise/GanttTimelineChart';
import { MetricKPIWidgetGroup, KPICardData } from '../components/enterprise/MetricKPIWidgetGroup';

export function ProductionSchedulingAPS() {
  const kpis: KPICardData[] = [
    { title: 'Overall Equipment Effectiveness (OEE)', value: '86.4%', change: '+3.8%', isPositive: true, icon: '⚙️', subtitle: 'Availability x Performance x Quality' },
    { title: 'Shop Floor Makespan Reduction', value: '-18.2%', change: 'Optimized', isPositive: true, icon: '⏱️', subtitle: 'Finite capacity constraint leveling' },
    { title: 'Machine Setup Time Saved', value: '46 Hours', change: '-22%', isPositive: true, icon: '🔧', subtitle: 'Changeover matrix sequencing' },
    { title: 'Critical Path Bottlenecks', value: '1 Node', change: 'Controlled', isPositive: true, icon: '⚠️', subtitle: '5-Axis CNC Milling Cell' },
  ];

  const tasks: GanttTask[] = [
    { id: '1', name: 'WO-8841 Precision Rotor Milling', workCenter: 'CNC Milling Cell #1', startHour: 1, durationHours: 6, progressPct: 80, status: 'RUNNING' },
    { id: '2', name: 'WO-8842 Heat Treatment Hardening', workCenter: 'Induction Furnace #2', startHour: 7, durationHours: 4, progressPct: 100, status: 'COMPLETED' },
    { id: '3', name: 'WO-8843 Stator Coil Winding', workCenter: 'Automated Winding Line', startHour: 2, durationHours: 8, progressPct: 40, status: 'RUNNING' },
    { id: '4', name: 'WO-8844 Final Dynamic Balancing', workCenter: 'Balancing & QC Rig', startHour: 12, durationHours: 5, progressPct: 0, status: 'SCHEDULED' },
    { id: '5', name: 'WO-8845 Die Changeover & Clean', workCenter: 'Injection Molding #4', startHour: 8, durationHours: 3, progressPct: 0, status: 'DELAYED' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 dark:text-white">Production Scheduling (APS)</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Finite capacity shop floor scheduling, changeover sequence optimization, and real-time Gantt execution</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-sm transition-colors">
          ⚡ Run APS Optimization Engine
        </button>
      </div>

      <MetricKPIWidgetGroup cards={kpis} />

      <GanttTimelineChart tasks={tasks} />
    </div>
  );
}
