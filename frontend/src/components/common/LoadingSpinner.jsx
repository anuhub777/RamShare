import React from 'react';

export const LoadingSpinner = ({ label = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center p-12 text-slate-400">
    <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent mb-3" />
    <span className="text-sm">{label}</span>
  </div>
);
