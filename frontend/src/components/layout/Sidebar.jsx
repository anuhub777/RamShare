import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Server, UploadCloud, Layers,
  CreditCard, UserCheck, Shield
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { path: '/consumer', label: 'Consumer Hub', icon: UploadCloud },
  { path: '/provider', label: 'Provider Hub', icon: Server },
  { path: '/marketplace', label: 'Marketplace', icon: Layers },
  { path: '/submit-job', label: 'Submit Workload', icon: UploadCloud },
  { path: '/jobs', label: 'Job History', icon: Layers },
  { path: '/credits', label: 'Credit Wallet', icon: CreditCard },
  { path: '/profile', label: 'Profile & Settings', icon: UserCheck },
];

export const Sidebar = () => {
  return (
    <aside className="w-64 border-r border-slate-800 bg-navy-900/60 p-4 hidden md:flex flex-col justify-between">
      <nav className="space-y-1.5">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3 mb-3">
          Navigation
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-1">
          <Shield className="h-4 w-4" /> Docker Sandbox Active
        </div>
        <p className="text-xs text-slate-400">
          Workloads run strictly isolated via CPU/RAM quota and dropped capabilities.
        </p>
      </div>
    </aside>
  );
};
