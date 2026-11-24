import React from 'react';
import { Link } from 'react-router-dom';
import { Cpu, HardDrive, ShieldCheck, CheckCircle2, XCircle } from 'lucide-react';

export const ProviderCard = ({ provider }) => {
  return (
    <div className="card hover:border-slate-700 transition">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-white text-base">{provider.machine_name}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{provider.os_type} {provider.architecture}</p>
        </div>
        <span className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${
          provider.is_online ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
        }`}>
          {provider.is_online ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
          {provider.is_online ? 'ONLINE' : 'OFFLINE'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-slate-800 text-xs">
        <div>
          <span className="text-slate-400 flex items-center gap-1">
            <Cpu className="h-3.5 w-3.5 text-blue-400" /> Avail CPU
          </span>
          <span className="font-semibold text-white mt-1 block">{provider.available_cpu_percent}%</span>
        </div>
        <div>
          <span className="text-slate-400 flex items-center gap-1">
            <HardDrive className="h-3.5 w-3.5 text-cyan-400" /> Avail RAM
          </span>
          <span className="font-semibold text-white mt-1 block">{provider.available_ram_mb} MB</span>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-1 text-xs text-slate-400">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Reliability: {(provider.reliability_score * 100).toFixed(0)}%</span>
        </div>
        <Link to={`/marketplace/${provider.id || provider.provider_id}`} className="text-xs text-blue-400 hover:text-blue-300 font-medium">
          View Details &rarr;
        </Link>
      </div>
    </div>
  );
};
