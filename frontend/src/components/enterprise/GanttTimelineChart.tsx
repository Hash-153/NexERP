import React from 'react';

export interface GanttTask {
  id: string;
  name: string;
  workCenter: string;
  startHour: number; // 0 to 24
  durationHours: number;
  progressPct: number;
  status: 'SCHEDULED' | 'RUNNING' | 'COMPLETED' | 'DELAYED';
}

interface GanttTimelineChartProps {
  tasks: GanttTask[];
  title?: string;
  totalShiftHours?: number;
}

export function GanttTimelineChart({ tasks, title = 'Shop Floor Production Gantt Schedule', totalShiftHours = 24 }: GanttTimelineChartProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RUNNING': return 'bg-blue-600 border-blue-700 text-white';
      case 'COMPLETED': return 'bg-emerald-600 border-emerald-700 text-white';
      case 'DELAYED': return 'bg-rose-600 border-rose-700 text-white';
      default: return 'bg-amber-500 border-amber-600 text-white';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">{title}</h3>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-blue-600"></span> Running</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-600"></span> Completed</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-amber-500"></span> Scheduled</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-rose-600"></span> Delayed</span>
        </div>
      </div>

      {/* Timeline Hour Scale Header */}
      <div className="relative border-b border-slate-200 dark:border-slate-800 pb-2 mb-4 grid grid-cols-12 text-xs text-slate-400 font-mono text-center">
        {Array.from({ length: 12 }, (_, i) => (
          <div key={i}>{String(i * 2).padStart(2, '0')}:00</div>
        ))}
      </div>

      {/* Task Rows */}
      <div className="space-y-3">
        {tasks.map(task => {
          const leftPct = (task.startHour / totalShiftHours) * 100;
          const widthPct = Math.min((task.durationHours / totalShiftHours) * 100, 100 - leftPct);

          return (
            <div key={task.id} className="flex items-center gap-4 text-sm">
              <div className="w-40 flex-shrink-0 font-medium text-slate-800 dark:text-slate-200 truncate">
                {task.workCenter}
                <div className="text-xs text-slate-400">{task.name}</div>
              </div>
              <div className="flex-1 bg-slate-100 dark:bg-slate-800/80 rounded-lg h-10 relative overflow-hidden">
                <div
                  className={`absolute top-1 bottom-1 rounded-md shadow-sm flex items-center px-3 text-xs font-semibold border ${getStatusColor(
                    task.status
                  )}`}
                  style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                >
                  <span className="truncate">{task.name} ({task.durationHours}h)</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
