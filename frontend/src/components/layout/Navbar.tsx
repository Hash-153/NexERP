import React from 'react';
import { Bell, Search, User, LogOut, Building2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Search Bar */}
      <div className="relative w-96">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search items, invoices, customers, BOMs..."
          className="w-full pl-9 pr-4 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
        />
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-4">
        {/* Tenant Indicator */}
        <div className="flex items-center space-x-2 bg-slate-800/60 border border-slate-700 px-3 py-1.5 rounded-lg text-xs text-slate-300">
          <Building2 className="w-3.5 h-3.5 text-brand-500" />
          <span className="font-semibold text-white">Apex Dynamics Industrial Corp</span>
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded text-[10px]">HQ Live</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-500 rounded-full animate-pulse" />
        </button>

        {/* User Profile */}
        <div className="flex items-center space-x-3 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center text-brand-400 font-semibold text-xs">
            {user ? `${user.first_name[0]}${user.last_name[0]}` : 'AD'}
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-medium text-slate-200">{user ? `${user.first_name} ${user.last_name}` : 'Admin User'}</p>
            <p className="text-[10px] text-slate-400">{user?.roles?.[0] || 'SuperAdmin'}</p>
          </div>
          <button
            onClick={logout}
            title="Sign Out"
            className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors ml-1"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
