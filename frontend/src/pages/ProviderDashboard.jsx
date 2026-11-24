import React, { useEffect, useState } from 'react';
import { providersApi } from '../api/providers';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/common/StatCard';
import { Server, Cpu, HardDrive, Terminal, CheckCircle2, XCircle, Download, Copy, Check } from 'lucide-react';

export const ProviderDashboard = () => {
  const { user } = useAuth();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  const installCmd = `curl -sSL ${window.location.origin}/install.sh | bash`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(installCmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    let isMounted = true;
    const fetchProviders = async () => {
      try {
        const res = await providersApi.list(false);
        const myNodes = res.data.providers?.filter((p) => p.user_id === user?.id) || [];
        if (isMounted) setProviders(myNodes);
      } catch (err) {
        console.error(err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchProviders();
    const interval = setInterval(fetchProviders, 5000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [user]);

  const toggleSharing = async (providerId, currentStatus) => {
    try {
      await providersApi.setAvailability(providerId, !currentStatus);
      setProviders(providers.map(p => p.id === providerId ? { ...p, is_sharing: !currentStatus } : p));
    } catch (e) {
      alert('Failed to update availability');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Provider Hub</h1>
        <p className="text-sm text-slate-400">Contribute unused compute resources and earn marketplace credits.</p>
      </div>

      {/* How to Install Provider Agent Card */}
      <div className="card bg-gradient-to-r from-blue-900/30 via-navy-900 to-navy-900 border-blue-500/20">
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
                <Terminal className="h-4 w-4" /> Become a Compute Provider
              </div>
              <h2 className="text-lg font-bold text-white">Install the RAMShare Agent on your computer</h2>
              <p className="text-sm text-slate-400 mt-1 max-w-xl">
                The agent safely allocates unused CPU cores and RAM while running workloads inside restricted Docker containers.
              </p>
            </div>
            <a
              href="/providers/agent/download"
              download="ramshare-provider-agent.zip"
              className="btn-secondary flex items-center justify-center gap-2 text-sm whitespace-nowrap self-start md:self-auto"
            >
              <Download className="h-4 w-4" /> Download Agent (.zip)
            </a>
          </div>

          <div className="pt-2 border-t border-slate-800">
            <span className="text-xs font-semibold text-slate-300 block mb-2">
              ⚡ Quick Terminal Install (macOS / Linux):
            </span>
            <div className="flex items-center justify-between gap-3 bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-xs text-slate-200 overflow-x-auto">
              <code>{installCmd}</code>
              <button
                onClick={copyToClipboard}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 transition shrink-0"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Connected Nodes" value={providers.length} subtitle="Registered computers" icon={Server} color="blue" />
        <StatCard title="Online Sharing Nodes" value={providers.filter(p => p.is_online && p.is_sharing).length} subtitle="Accepting workloads" icon={CheckCircle2} color="emerald" />
        <StatCard title="Total Capacity" value={`${providers.reduce((acc, p) => acc + (p.total_ram_mb || 0), 0) / 1024} GB`} subtitle="Allocated RAM" icon={HardDrive} color="cyan" />
      </div>

      <div className="card">
        <h2 className="text-lg font-bold text-white mb-4">Your Registered Provider Nodes</h2>
        {providers.length === 0 ? (
          <div className="text-center py-10 text-slate-400">
            <Server className="h-10 w-10 mx-auto text-slate-600 mb-2" />
            <p className="font-semibold text-slate-300">No compute nodes connected yet</p>
            <p className="text-xs text-slate-500 mt-1">Start the provider agent on your PC using the command above to link your machine.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {providers.map((p) => (
              <div key={p.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-white text-base">{p.machine_name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      p.is_online ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-500'
                    }`}>
                      {p.is_online ? 'ONLINE' : 'OFFLINE'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {p.os_type} {p.os_version} ({p.architecture}) &bull; {p.total_cpu_cores} Cores &bull; {p.total_ram_mb}MB Total RAM
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Limits: Up to {p.max_cpu_percent}% CPU, {p.max_ram_mb}MB RAM, Max {p.max_concurrent_jobs} concurrent jobs
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleSharing(p.id, p.is_sharing)}
                    className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition ${
                      p.is_sharing ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:bg-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30'
                    }`}
                  >
                    {p.is_sharing ? 'Pause Sharing' : 'Start Sharing'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
