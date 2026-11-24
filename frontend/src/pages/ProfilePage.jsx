import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Shield, Coins, CheckCircle2 } from 'lucide-react';

export const ProfilePage = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Profile & Settings</h1>
        <p className="text-sm text-slate-400">Account credentials, roles, and safety configurations.</p>
      </div>

      <div className="card space-y-6">
        <div className="flex items-center gap-4 pb-6 border-b border-slate-800">
          <div className="h-16 w-16 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center font-bold text-2xl text-blue-400">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{user?.username}</h2>
            <p className="text-sm text-slate-400">{user?.email}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-xs text-slate-400 uppercase font-semibold">User ID</span>
            <p className="font-mono text-xs text-slate-300 mt-1">{user?.id}</p>
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase font-semibold">Roles</span>
            <div className="flex gap-1.5 mt-1">
              {user?.roles?.map(r => (
                <span key={r} className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
                  {r}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800">
          <h3 className="font-bold text-white text-sm mb-3">Security & Sandboxing</h3>
          <div className="flex items-start gap-3 p-3 rounded-xl border border-slate-800 bg-slate-950/60">
            <Shield className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="text-xs font-semibold text-white">Safe Execution Policy</span>
              <p className="text-xs text-slate-400 mt-0.5">
                Workloads run as user <code>nobody</code>, dropped capabilities, no host network, and memory/CPU quotas.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
