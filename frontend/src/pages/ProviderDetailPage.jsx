import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { providersApi } from '../api/providers';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Cpu, HardDrive, ShieldCheck, CheckCircle2, ArrowLeft, UploadCloud } from 'lucide-react';

export const ProviderDetailPage = () => {
  const { providerId } = useParams();
  const [provider, setProvider] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProvider = async () => {
      try {
        const res = await providersApi.get(providerId);
        setProvider(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProvider();
  }, [providerId]);

  if (loading) return <LoadingSpinner label="Loading node details..." />;
  if (!provider) return <div className="card p-6 text-center text-red-400">Provider machine not found</div>;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Link to="/marketplace" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white">
        <ArrowLeft className="h-4 w-4" /> Back to Marketplace
      </Link>

      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-white">{provider.machine_name}</h1>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                provider.is_online ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
              }`}>
                {provider.is_online ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Registered Node ID: {provider.id}</p>
          </div>
          <Link to="/submit-job" className="btn-primary flex items-center gap-2 text-sm">
            <UploadCloud className="h-4 w-4" /> Submit Workload
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div>
            <span className="text-xs text-slate-400">OS Architecture</span>
            <p className="font-semibold text-white mt-1">{provider.os_type} ({provider.architecture})</p>
          </div>
          <div>
            <span className="text-xs text-slate-400">Total CPU Cores</span>
            <p className="font-semibold text-white mt-1">{provider.total_cpu_cores} Cores</p>
          </div>
          <div>
            <span className="text-xs text-slate-400">Total Installed RAM</span>
            <p className="font-semibold text-white mt-1">{provider.total_ram_mb} MB</p>
          </div>
          <div>
            <span className="text-xs text-slate-400">Reliability Score</span>
            <p className="font-semibold text-emerald-400 mt-1">{(provider.reliability_score * 100).toFixed(0)}%</p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-800">
          <h2 className="text-base font-bold text-white mb-3">Live Resource Capacity</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
              <div className="text-xs text-slate-400 mb-1">Available CPU Capacity</div>
              <div className="text-2xl font-bold text-blue-400">{provider.available_cpu_percent}%</div>
              <div className="text-xs text-slate-500 mt-1">Provider limit capped at {provider.max_cpu_percent}%</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
              <div className="text-xs text-slate-400 mb-1">Available RAM Capacity</div>
              <div className="text-2xl font-bold text-cyan-400">{provider.available_ram_mb} MB</div>
              <div className="text-xs text-slate-500 mt-1">Provider allocation max: {provider.max_ram_mb} MB</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
