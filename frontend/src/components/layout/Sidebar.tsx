import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Landmark,
  Receipt,
  FileSpreadsheet,
  Boxes,
  Truck,
  TrendingUp,
  Factory,
  ShieldCheck,
  Users,
  Briefcase,
  BarChart3,
  Globe,
  ArrowRightLeft,
  Calculator,
  Activity,
  Award,
  Layers,
  Shield,
  Percent,
  Tag,
  Network
} from 'lucide-react';

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { label: 'Executive Dashboard', path: '/', icon: LayoutDashboard },
  { label: 'Financials & GL', path: '/financials', icon: Landmark },
  { label: 'Accounts Payable', path: '/accounts-payable', icon: Receipt },
  { label: 'Accounts Receivable', path: '/accounts-receivable', icon: FileSpreadsheet },
  { label: 'Inventory & WMS', path: '/inventory', icon: Boxes },
  { label: 'Procurement & SCM', path: '/procurement', icon: Truck },
  { label: 'Sales & CRM', path: '/sales', icon: TrendingUp },
  { label: 'Manufacturing & MRP', path: '/manufacturing', icon: Factory },
  { label: 'Quality Control', path: '/quality', icon: ShieldCheck },
  { label: 'Human Resources', path: '/hr', icon: Users },
  { label: 'Projects & PSA', path: '/projects', icon: Briefcase },
  { label: 'Analytics & BI', path: '/analytics', icon: BarChart3 },
];

const advancedViews: NavItem[] = [
  { label: 'FX Revaluation', path: '/financials/revaluation', icon: Globe },
  { label: 'Bank Reconciliation', path: '/financials/reconciliation', icon: ArrowRightLeft },
  { label: 'Fixed Assets (PPE)', path: '/financials/fixed-assets', icon: Calculator },
  { label: 'RFQ Sealed Bids', path: '/procurement/rfq', icon: Award },
  { label: 'Finite APS Gantt', path: '/manufacturing/gantt', icon: Layers },
  { label: 'SPC & Six Sigma', path: '/quality/spc', icon: Activity },
  { label: 'Pricing Matrix', path: '/sales/pricing', icon: Tag },
  { label: 'Pay Equity Bands', path: '/hr/compensation', icon: Percent },
  { label: 'Lot Pedigree Trace', path: '/inventory/genealogy', icon: Network },
  { label: 'SOX Audit Trail', path: '/governance/audit', icon: Shield },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 space-x-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-sky-400 flex items-center justify-center font-bold text-white shadow-lg shadow-brand-500/20">
          N
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight text-white flex items-center">
            Nex<span className="text-brand-500">ERP</span>
          </h1>
          <p className="text-[10px] text-slate-400 font-mono">v1.0.0 Enterprise</p>
        </div>
      </div>

      {/* Nav Menu Links */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-4">
        <div>
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Core Domains</p>
          <div className="space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        </div>

        <div>
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Advanced Engines & GRC</p>
          <div className="space-y-0.5">
            {advancedViews.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </div>
        </div>
      </div>

      {/* Bottom Footer Status */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Ledger Invariant</span>
          </span>
          <span className="font-mono text-emerald-400 font-semibold">100% Balanced</span>
        </div>
      </div>
    </aside>
  );
};
