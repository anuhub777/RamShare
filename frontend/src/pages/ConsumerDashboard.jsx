import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { StatCard } from '../components/common/StatCard';
import { JobStatusBadge } from '../components/jobs/JobStatusBadge';
import { UploadCloud, Layers, CheckCircle2, Clock, ArrowRight } from 'lucide-react';

export const ConsumerDashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await jobsApi.list();
        setJobs(res.data.jobs || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const runningCount = jobs.filter(j => ['MATCHING', 'ASSIGNED', 'RUNNING'].includes(j.status)).length;
  const completedCount = jobs.filter(j => j.status === 'COMPLETED').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Consumer Hub</h1>
          <p className="text-sm text-slate-400">Launch Docker computational jobs on peer provider computers.</p>
        </div>
        <Link to="/submit-job" className="btn-primary flex items-center gap-2 text-sm">
          <UploadCloud className="h-4 w-4" /> New Workload
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Active Workloads" value={runningCount} subtitle="In progress or matching" icon={Clock} color="blue" />
        <StatCard title="Completed Jobs" value={completedCount} subtitle="Outputs ready for retrieval" icon={CheckCircle2} color="emerald" />
        <StatCard title="Total Submissions" value={jobs.length} subtitle="Lifetime consumer jobs" icon={Layers} color="purple" />
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">Your Submitted Workloads</h2>
          <Link to="/jobs" className="text-xs text-blue-400 hover:text-blue-300 font-medium">Full History &rarr;</Link>
        </div>

        {jobs.length === 0 ? (
          <div className="text-center py-10 text-slate-400">
            <UploadCloud className="h-10 w-10 mx-auto text-slate-600 mb-2" />
            <p className="font-semibold text-slate-300">No jobs submitted yet</p>
            <p className="text-xs text-slate-500 mt-1">Submit your first benchmark or ML workload to get started.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {jobs.map((j) => (
              <div key={j.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{j.job_name}</span>
                    <JobStatusBadge status={j.status} />
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {j.workload_type} &bull; {j.required_ram_mb}MB RAM &bull; {j.required_cpu_cores} Cores &bull; Max {j.max_execution_time}s
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold text-amber-400">{j.estimated_credits} credits</span>
                  <Link to={`/jobs/${j.id}`} className="btn-secondary text-xs py-1.5">View</Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
