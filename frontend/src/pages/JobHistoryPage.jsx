import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { JobStatusBadge } from '../components/jobs/JobStatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Layers } from 'lucide-react';

export const JobHistoryPage = () => {
  const [jobs, setJobs] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await jobsApi.list(statusFilter || null);
        setJobs(res.data.jobs || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, [statusFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Workload History</h1>
          <p className="text-sm text-slate-400">Complete historical record of submitted workloads.</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-800 bg-navy-900 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
        >
          <option value="">All Statuses</option>
          <option value="COMPLETED">Completed</option>
          <option value="RUNNING">Running</option>
          <option value="FAILED">Failed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>

      <div className="card">
        {loading ? (
          <LoadingSpinner label="Loading history..." />
        ) : jobs.length === 0 ? (
          <p className="text-sm text-slate-400 py-10 text-center">No jobs found.</p>
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
                  <th className="pb-3 font-semibold">Submitted</th>
                  <th className="pb-3 font-semibold text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {jobs.map((j) => (
                  <tr key={j.id} className="hover:bg-slate-900/40">
                    <td className="py-3 font-medium text-white">{j.job_name}</td>
                    <td className="py-3 text-slate-400 text-xs">{j.workload_type}</td>
                    <td className="py-3"><JobStatusBadge status={j.status} /></td>
                    <td className="py-3 text-slate-300 text-xs">{j.required_ram_mb}MB / {j.required_cpu_cores}c</td>
                    <td className="py-3 text-amber-400 font-medium text-xs">{j.actual_credits || j.estimated_credits} cr</td>
                    <td className="py-3 text-slate-400 text-xs">{new Date(j.created_at).toLocaleDateString()}</td>
                    <td className="py-3 text-right">
                      <Link to={`/jobs/${j.id}`} className="text-xs text-blue-400 hover:text-blue-300 font-medium">View</Link>
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
