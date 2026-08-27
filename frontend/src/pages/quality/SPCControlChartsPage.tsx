import React, { useState } from 'react';
import { Activity, ShieldCheck, AlertTriangle, Cpu, TrendingUp, CheckCircle } from 'lucide-react';

export const SPCControlChartsPage: React.FC = () => {
  const [selectedWorkCenter, setSelectedWorkCenter] = useState('WC-CNC-01');

  const xbarData = [
    { subgroup: 1, mean: 10.10, ucl: 10.35, lcl: 9.85, cl: 10.10, isViolation: false },
    { subgroup: 2, mean: 10.15, ucl: 10.35, lcl: 9.85, cl: 10.10, isViolation: false },
    { subgroup: 3, mean: 10.08, ucl: 10.35, lcl: 9.85, cl: 10.10, isViolation: false },
    { subgroup: 4, mean: 10.22, ucl: 10.35, lcl: 9.85, cl: 10.10, isViolation: false },
    { subgroup: 5, mean: 10.12, ucl: 10.35, lcl: 9.85, cl: 10.10, isViolation: false },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Statistical Process Control (SPC) & Six Sigma</h1>
          <p className="text-sm text-slate-500">Real-time Shewhart X-bar / R control charts, process capability indices (Cp, Cpk), and Western Electric anomaly detection.</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedWorkCenter}
            onChange={(e) => setSelectedWorkCenter(e.target.value)}
            className="px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-900 dark:text-white"
          >
            <option value="WC-CNC-01">CNC Milling Cell 1 (Shaft Diameter)</option>
            <option value="WC-SMT-02">Surface Mount SMT Line (Solder Thickness)</option>
            <option value="WC-INJ-04">Injection Molding (Wall Thickness)</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Process Capability ($C_p$)</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">1.82</p>
          <span className="text-xs text-emerald-600 font-medium">World-Class Spread</span>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Centered Capability (Cpk)</span>
          <p className="text-2xl font-bold text-emerald-600 mt-1">1.68</p>
          <span className="text-xs text-emerald-600 font-medium">Six Sigma Quality (&gt;1.67)</span>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Estimated Defect PPM</span>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">3.4 PPM</p>
          <span className="text-xs text-slate-500">Near Zero Defects</span>
        </div>
        <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
          <span className="text-xs text-slate-500 font-medium">Process State</span>
          <div className="flex items-center gap-1.5 mt-1 text-emerald-600 font-bold text-lg">
            <CheckCircle className="w-5 h-5" /> In Statistical Control
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-4">
        <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-600" /> X-Bar Subgroup Mean Control Chart
        </h3>

        {/* Visual Simulated SPC Chart Points */}
        <div className="h-64 border border-dashed border-slate-200 dark:border-slate-700 rounded-lg p-4 flex items-end justify-between relative bg-slate-50/50 dark:bg-slate-900/30">
          <div className="absolute top-4 left-4 text-xs font-mono text-rose-500 font-semibold">UCL = 10.350 mm</div>
          <div className="absolute top-1/2 left-4 -translate-y-1/2 text-xs font-mono text-indigo-500 font-semibold">CL (Grand Mean) = 10.100 mm</div>
          <div className="absolute bottom-4 left-4 text-xs font-mono text-rose-500 font-semibold">LCL = 9.850 mm</div>

          {xbarData.map((pt, i) => (
            <div key={i} className="flex flex-col items-center gap-2 z-10">
              <span className="text-xs font-mono text-slate-600 dark:text-slate-400 font-semibold">{pt.mean.toFixed(2)}</span>
              <div className="w-4 h-4 rounded-full bg-indigo-600 border-2 border-white dark:border-slate-800 shadow-sm"></div>
              <span className="text-xs text-slate-500">SG #{pt.subgroup}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
