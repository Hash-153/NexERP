import React from 'react';

export interface KPICardData {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon?: string;
  sparklineData?: number[];
  subtitle?: string;
  badgeColor?: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple';
}

interface MetricKPIWidgetGroupProps {
  cards: KPICardData[];
}

export function MetricKPIWidgetGroup({ cards }: MetricKPIWidgetGroupProps) {
  const getBadgeClass = (color: string = 'blue') => {
    switch (color) {
      case 'emerald': return 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800';
      case 'amber': return 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800';
      case 'rose': return 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800';
      case 'purple': return 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-400 dark:border-purple-800';
      default: return 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-800';
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              {card.title}
            </span>
            {card.icon && (
              <span className={`p-2 rounded-lg border text-lg ${getBadgeClass(card.badgeColor)}`}>
                {card.icon}
              </span>
            )}
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              {card.value}
            </div>
            <div className="mt-2 flex items-center gap-2">
              {card.change && (
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded-full flex items-center gap-0.5 ${
                    card.isPositive !== false
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                      : 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
                  }`}
                >
                  {card.isPositive !== false ? '↑' : '↓'} {card.change}
                </span>
              )}
              {card.subtitle && (
                <span className="text-xs text-slate-400 dark:text-slate-500 truncate">
                  {card.subtitle}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
