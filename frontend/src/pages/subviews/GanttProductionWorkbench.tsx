import React from 'react';

export function GanttProductionWorkbench() {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">Shop Floor Finite Capacity Gantt Workbench</h3>
          <p className="text-xs text-slate-500">Live multi-machine Gantt scheduling with drag-drop critical path adjustment</p>
        </div>
        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full">
          OEE: 86.4%
        </span>
      </div>

      <div className="space-y-3 pt-2">
        <div className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <div className="w-48 font-bold text-xs text-slate-700 dark:text-slate-300">CNC Milling Cell #1</div>
          <div className="flex-1 bg-slate-200 dark:bg-slate-700 rounded h-6 relative overflow-hidden">
            <div className="absolute left-0 w-3/5 bg-blue-600 h-full text-white text-[10px] font-bold flex items-center px-2">
              WO-8841 (6.0h - 80% Complete)
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <div className="w-48 font-bold text-xs text-slate-700 dark:text-slate-300">Induction Furnace #2</div>
          <div className="flex-1 bg-slate-200 dark:bg-slate-700 rounded h-6 relative overflow-hidden">
            <div className="absolute left-[60%] w-1/4 bg-emerald-600 h-full text-white text-[10px] font-bold flex items-center px-2">
              WO-8842 (4.0h Heat Treat)
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <div className="w-48 font-bold text-xs text-slate-700 dark:text-slate-300">Automated Winding Line</div>
          <div className="flex-1 bg-slate-200 dark:bg-slate-700 rounded h-6 relative overflow-hidden">
            <div className="absolute left-[10%] w-2/5 bg-amber-500 h-full text-white text-[10px] font-bold flex items-center px-2">
              WO-8843 (8.0h Stator Coil)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
