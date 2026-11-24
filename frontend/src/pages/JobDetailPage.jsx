import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { JobStatusBadge } from '../components/jobs/JobStatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ArrowLeft, Cpu, HardDrive, Clock, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';

export const JobDetailPage = () => {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchJob = async () => {
    try {
      const res = await jobsApi.get(jobId);
      setJob(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJob();
    const interval = setInterval(fetchJob, 4000); // Polling for status updates
    return () => clearInterval(interval);
  }, [jobId]);

  const handleCancel = async () => {
    try {
      await jobsApi.cancel(jobId);
      fetchJob();
    } catch (e) {
      alert('Could not cancel job');
    }
  };

  if (loading) return <LoadingSpinner label="Fetching job state..." />;
  if (!job) return <div className="card text-center text-red-400">Job not found</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/jobs" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white">
        <ArrowLeft className="h-4 w-4" /> Back to Jobs
      </Link>

      <div className="card space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-white">{job.job_name}</h1>
              <JobStatusBadge status={job.status} />
            </div>
            <p className="text-xs text-slate-400 mt-1">ID: {job.id} &bull; Type: {job.workload_type}</p>
          </div>

          <div className="flex items-center gap-2">
            {['PENDING', 'QUEUED', 'MATCHING'].includes(job.status) && (
              <button onClick={handleCancel} className="btn-secondary text-xs text-red-400 hover:text-red-300">
                Cancel Job
              </button>
            )}
            <button onClick={fetchJob} className="btn-secondary text-xs p-2" title="Refresh">
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <span className="text-xs text-slate-400">Required RAM</span>
            <p className="font-semibold text-white mt-1">{job.required_ram_mb} MB</p>
          </div>
          <div>
            <span className="text-xs text-slate-400">Required CPU</span>
            <p className="font-semibold text-white mt-1">{job.required_cpu_cores} Cores</p>
          </div>
          <div>
            <span className="text-xs text-slate-400">Assigned Provider</span>
            <p className="font-semibold text-white mt-1">{job.provider_id || 'Awaiting match...'}</p>
          </div>
          <div>
            <span className="text-xs text-slate-400">Credits Settled</span>
            <p className="font-semibold text-amber-400 mt-1">{job.actual_credits || job.estimated_credits} cr</p>
          </div>
        </div>

        {/* Execution Output Box */}
        {job.result_summary && (
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-bold text-emerald-400 mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" /> Execution Result Output
            </h3>
            <pre className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs font-mono text-slate-200 overflow-x-auto whitespace-pre-wrap">
              {job.result_summary}
            </pre>
          </div>
        )}

        {job.error_message && (
          <div className="pt-4 border-t border-slate-800">
            <h3 className="text-sm font-bold text-red-400 mb-2 flex items-center gap-1.5">
              <XCircle className="h-4 w-4" /> Execution Error Log
            </h3>
            <pre className="bg-slate-950 p-4 rounded-xl border border-red-500/20 text-xs font-mono text-red-300 overflow-x-auto whitespace-pre-wrap">
              {job.error_message}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
