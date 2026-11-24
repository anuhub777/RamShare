import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { marketplaceApi } from '../api/marketplace';
import { jobsApi } from '../api/jobs';
import { StatCard } from '../components/common/StatCard';
import { JobStatusBadge } from '../components/jobs/JobStatusBadge';
import { ResourceChart } from '../components/charts/ResourceChart';
import { Server, Cpu, HardDrive, Layers, UploadCloud, ArrowRight } from 'lucide-react';

export const DashboardPage = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      // 1. Fetch public marketplace statistics
      try {
        const statsRes = await marketplaceApi.getStatistics();
        if (isMounted && statsRes?.data) {
          setStats(statsRes.data);
        }
      } catch (err) {
        console.error('Failed to load marketplace statistics', err);
      }

      // 2. Fetch user's recent jobs
      try {
        const jobsRes = await jobsApi.list();
        if (isMounted && jobsRes?.data?.jobs) {
          setRecentJobs(jobsRes.data.jobs.slice(0, 5));
        }
      } catch (err) {
        console.error('Failed to load user jobs', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchData();

    // Live refresh telemetry every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Marketplace Overview</h1>
          <p className="text-sm text-slate-400">Welcome, {user?.username}. System network telemetry & active workloads.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/submit-job" className="btn-primary flex items-center gap-2 text-sm">
            <UploadCloud className="h-4 w-4" /> Submit Workload
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Online Providers"
          value={stats ? `${stats.online_providers} / ${stats.total_providers}` : '0 / 0'}
          subtitle="Ready to accept workloads"
          icon={Server}
          color="emerald"
        />
        <StatCard
          title="Network RAM Available"
          value={stats ? `${(stats.total_available_ram_mb / 1024).toFixed(1)} GB` : '0 GB'}
          subtitle="Distributed capacity"
          icon={HardDrive}
          color="cyan"
        />
        <StatCard
          title="Total CPU Cores"
          value={stats ? stats.total_available_cpu_cores : 0}
          subtitle="Available for allocation"
          icon={Cpu}
          color="blue"
        />
        <StatCard
          title="Active Workloads"
          value={stats ? stats.active_jobs : 0}
          subtitle={`${stats?.completed_jobs || 0} completed successfully`}
          icon={Layers}
          color="amber"
        />
      </div>

      {/* Telemetry Chart & Quick Actions */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-white">Resource Utilization Trend</h2>
            <span className="text-xs text-slate-400">Aggregated provider averages</span>
          </div>
          <ResourceChart />
        </div>

        <div className="card flex flex-col justify-between">
          <div>
            <h2 className="font-bold text-white mb-2">Quick Navigation</h2>
            <p className="text-xs text-slate-400 mb-4">Choose your interaction mode</p>
            <div className="space-y-3">
              <Link to="/consumer" className="block p-3 rounded-lg border border-slate-800 bg-slate-900/60 hover:border-blue-500/40 transition">
                <div className="font-semibold text-sm text-blue-400">Consumer Portal</div>
                <div className="text-xs text-slate-400 mt-0.5">Submit benchmarks & check outputs</div>
              </Link>
              <Link to="/provider" className="block p-3 rounded-lg border border-slate-800 bg-slate-900/60 hover:border-emerald-500/40 transition">
                <div className="font-semibold text-sm text-emerald-400">Provider Portal</div>
                <div className="text-xs text-slate-400 mt-0.5">Install Desktop agent & earn credits</div>
              </Link>
              <Link to="/marketplace" className="block p-3 rounded-lg border border-slate-800 bg-slate-900/60 hover:border-cyan-500/40 transition">
                <div className="font-semibold text-sm text-cyan-400">Marketplace Nodes</div>
                <div className="text-xs text-slate-400 mt-0.5">Explore available compute rigs</div>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-bold text-white">Your Recent Workloads</h2>
          <Link to="/jobs" className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
            View All <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        {recentJobs.length === 0 ? (
          <p className="text-sm text-slate-400 py-6 text-center">No workloads submitted yet. Launch your first job!</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="pb-3 font-semibold">Job Name</th>
                  <th className="pb-3 font-semibold">Type</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">RAM / CPU</th>
                  <th className="pb-3 font-semibold">Cost</th>
                  <th className="pb-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentJobs.map((j) => (
                  <tr key={j.id} className="hover:bg-slate-900/40">
                    <td className="py-3 font-medium text-white">{j.job_name}</td>
                    <td className="py-3 text-slate-400 text-xs">{j.workload_type}</td>
                    <td className="py-3"><JobStatusBadge status={j.status} /></td>
                    <td className="py-3 text-slate-300 text-xs">{j.required_ram_mb}MB / {j.required_cpu_cores}c</td>
                    <td className="py-3 text-amber-400 font-medium text-xs">{j.estimated_credits} cr</td>
                    <td className="py-3 text-right">
                      <Link to={`/jobs/${j.id}`} className="text-xs text-blue-400 hover:text-blue-300 font-medium">Details</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
