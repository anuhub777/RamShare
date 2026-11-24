import React from 'react';

export const JobStatusBadge = ({ status }) => {
  const styles = {
    PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    QUEUED: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    MATCHING: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 animate-pulse',
    ASSIGNED: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    RUNNING: 'bg-blue-500/20 text-blue-300 border-blue-400/40 animate-pulse',
    COMPLETED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    FAILED: 'bg-red-500/10 text-red-400 border-red-500/30',
    CANCELLED: 'bg-slate-800 text-slate-400 border-slate-700',
    TIMED_OUT: 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[status] || 'bg-slate-800 text-slate-400'}`}>
      {status}
    </span>
  );
};
