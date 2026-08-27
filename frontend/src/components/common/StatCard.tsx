import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  change?: string;
  isPositive?: boolean;
  icon: React.ElementType;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  change,
  isPositive,
  icon: Icon
}) => {
  return (
    <div className="glass-panel p-5 rounded-xl border border-slate-800 relative overflow-hidden group hover:border-slate-700 transition-all">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
        <div className="p-2 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20 group-hover:scale-110 transition-transform">
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3">
        <h3 className="text-2xl font-bold font-mono tracking-tight text-white">{value}</h3>
        <div className="flex items-center space-x-2 mt-1.5">
          {change && (
            <span
              className={`flex items-center text-xs font-semibold ${
                isPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {isPositive ? <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> : <TrendingDown className="w-3.5 h-3.5 mr-0.5" />}
              {change}
            </span>
          )}
          {subtitle && <span className="text-xs text-slate-400">{subtitle}</span>}
        </div>
      </div>
    </div>
  );
};
