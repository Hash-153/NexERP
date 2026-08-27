import React, { useState } from 'react';
import { Calendar, Clock, Layers, Play, Settings, Wrench, CheckCircle } from 'lucide-react';

export const FiniteCapacityGanttPage: React.FC = () => {
  const [selectedShift, setSelectedShift] = useState('SHIFT_1');

  const mockWorkCenters = [
    {
      id: 'WC-01',
      name: 'CNC Milling Center A',
      capacityHours: 16.0,
      scheduledHours: 14.5,
      utilization: 90.6,
      jobs: [
        { jobNum: 'JC-1001', part: 'Flange Housing', start: '08:00', end: '12:30', duration: '4.5h', color: 'bg-indigo-500' },
        { jobNum: 'JC-1002', part: 'Titanium Rotor', start: '12:30', end: '18:30', duration: '6.0h', color: 'bg-emerald-500' },
        { jobNum: 'JC-1005', part: 'Shaft 25mm', start: '18:30', end: '22:30', duration: '4.0h', color: 'bg-amber-500' },
      ]
    },
    {
      id: 'WC-02',
      name: 'Automated SMT Line 1',
      capacityHours: 16.0,
      scheduledHours: 12.0,
      utilization: 75.0,
      jobs: [
        { jobNum: 'JC-1003', part: 'Control Board Main PCB', start: '08:00', end: '14:00', duration: '6.0h', color: 'bg-purple-500' },
        { jobNum: 'JC-1004', part: 'Power Supply Module', start: '14:00', end: '20:00', duration: '6.0h', color: 'bg-cyan-500' },
      ]
    },
    {
      id: 'WC-03',
      name: 'Final Assembly Cell B',
      capacityHours: 16.0,
      scheduledHours: 15.5,
      utilization: 96.8,
      jobs: [
        { jobNum: 'JC-1006', part: 'Actuator Assembly', start: '08:00', end: '16:00', duration: '8.0h', color: 'bg-rose-500' },
        { jobNum: 'JC-1007', part: 'Final Packout Box', start: '16:00', end: '23:30', duration: '7.5h', color: 'bg-blue-500' },
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Finite Capacity APS Scheduling & Work Center Gantt</h1>
          <p className="text-sm text-slate-500">Constraint-based finite capacity forward/backward dispatch sequencing across shop floor machine cells.</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition shadow-sm">
            <Play className="w-4 h-4" /> Run APS Optimization (EDD / SPT)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Plant Operating Capacity</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">48.0 Hours</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Scheduled Machine Load</span>
          <p className="text-2xl font-bold text-indigo-600 mt-1">42.0 Hours</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Overall Plant Utilization</span>
          <p className="text-2xl font-bold text-emerald-600 mt-1">87.5%</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Active Bottleneck Station</span>
          <p className="text-2xl font-bold text-amber-600 mt-1">Final Assembly B</p>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-600" /> Work Center Dispatch Timeline (Day 1 - 2 Shifts)
          </h3>
          <div className="flex gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-indigo-500"></span> Milling</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-purple-500"></span> SMT Electronics</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-rose-500"></span> Assembly</span>
          </div>
        </div>

        <div className="space-y-4">
          {mockWorkCenters.map((wc) => (
            <div key={wc.id} className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-slate-900 dark:text-white">{wc.name}</span>
                <span className="text-xs font-mono font-medium text-slate-600 dark:text-slate-400">
                  {wc.scheduledHours}h / {wc.capacityHours}h ({wc.utilization}%)
                </span>
              </div>

              {/* Visual Gantt Bar Track */}
              <div className="h-10 bg-slate-100 dark:bg-slate-900/60 rounded-lg p-1 flex gap-1.5 overflow-hidden border border-slate-200 dark:border-slate-800">
                {wc.jobs.map((job) => (
                  <div
                    key={job.jobNum}
                    className={`${job.color} text-white text-xs px-2.5 flex items-center justify-between rounded shadow-sm hover:opacity-90 transition cursor-pointer flex-1`}
                  >
                    <span className="font-bold font-mono">{job.jobNum}</span>
                    <span className="truncate ml-2 text-[11px] opacity-90">{job.part} ({job.duration})</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
