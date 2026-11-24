import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { creditsApi } from '../api/credits';
import { Cpu, HardDrive, Clock, UploadCloud, AlertCircle } from 'lucide-react';

export const SubmitWorkloadPage = () => {
  const [jobName, setJobName] = useState('');
  const [workloadType, setWorkloadType] = useState('CPU_BENCHMARK');
  const [requiredRamMb, setRequiredRamMb] = useState(512);
  const [requiredCpuCores, setRequiredCpuCores] = useState(1);
  const [maxExecutionTime, setMaxExecutionTime] = useState(120);
  const [inputParamsJson, setInputParamsJson] = useState('{\n  "iterations": 100000\n}');
  const [estimate, setEstimate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchEstimate = async () => {
      try {
        const res = await creditsApi.estimate({
          workload_type: workloadType,
          required_ram_mb: Number(requiredRamMb),
          required_cpu_cores: Number(requiredCpuCores),
          estimated_duration_seconds: Number(maxExecutionTime)
        });
        setEstimate(res.data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchEstimate();
  }, [workloadType, requiredRamMb, requiredCpuCores, maxExecutionTime]);

  const handleTypeChange = (type) => {
    setWorkloadType(type);
    if (type === 'CPU_BENCHMARK') {
      setInputParamsJson('{\n  "iterations": 100000\n}');
    } else if (type === 'MEMORY_BENCHMARK') {
      setInputParamsJson('{\n  "size_mb": 256\n}');
    } else if (type === 'DATA_PROCESSING') {
      setInputParamsJson('{\n  "dataset_name": "sample_batch_01",\n  "factor": 10\n}');
    } else if (type === 'ML_INFERENCE') {
      setInputParamsJson('{\n  "num_samples": 20\n}');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    let parsedParams = {};
    try {
      parsedParams = JSON.parse(inputParamsJson);
    } catch (err) {
      setError('Input Parameters must be valid JSON');
      return;
    }

    setLoading(true);
    try {
      const res = await jobsApi.submit({
        job_name: jobName,
        workload_type: workloadType,
        required_ram_mb: Number(requiredRamMb),
        required_cpu_cores: Number(requiredCpuCores),
        max_execution_time: Number(maxExecutionTime),
        input_params: parsedParams
      });
      navigate(`/jobs/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit workload');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Submit Computational Workload</h1>
        <p className="text-sm text-slate-400">Workload will be matched with an online peer computer and executed in Docker.</p>
      </div>

      <div className="card">
        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Workload Name</label>
            <input
              type="text"
              required
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              placeholder="e.g. Monte Carlo Matrix Benchmark"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Workload Type</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {['CPU_BENCHMARK', 'MEMORY_BENCHMARK', 'DATA_PROCESSING', 'ML_INFERENCE'].map((type) => (
                <button
                  type="button"
                  key={type}
                  onClick={() => handleTypeChange(type)}
                  className={`p-3 rounded-lg border text-xs font-semibold transition text-center ${
                    workloadType === type
                      ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                      : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {type.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1 flex items-center gap-1">
                <HardDrive className="h-3.5 w-3.5 text-cyan-400" /> Required RAM (MB)
              </label>
              <input
                type="number"
                min={128}
                max={8192}
                step={128}
                value={requiredRamMb}
                onChange={(e) => setRequiredRamMb(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1 flex items-center gap-1">
                <Cpu className="h-3.5 w-3.5 text-blue-400" /> CPU Cores
              </label>
              <input
                type="number"
                min={1}
                max={16}
                value={requiredCpuCores}
                onChange={(e) => setRequiredCpuCores(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1 flex items-center gap-1">
                <Clock className="h-3.5 w-3.5 text-amber-400" /> Max Time (Sec)
              </label>
              <input
                type="number"
                min={10}
                max={3600}
                step={30}
                value={maxExecutionTime}
                onChange={(e) => setMaxExecutionTime(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-white focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Input Parameters (JSON)</label>
            <textarea
              rows={4}
              value={inputParamsJson}
              onChange={(e) => setInputParamsJson(e.target.value)}
              className="w-full font-mono text-xs rounded-lg border border-slate-700 bg-slate-950 p-3 text-cyan-300 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Pricing Estimation Box */}
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider">Estimated Cost</span>
              <div className="text-xl font-bold text-amber-400 mt-0.5">
                {estimate?.estimated_credits || 0} Credits
              </div>
            </div>
            <div className="text-xs text-slate-500 text-right">
              Atomic hold on submission &bull; Refunded if failed
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            <UploadCloud className="h-4 w-4" />
            {loading ? 'Submitting to Matchmaker...' : 'Submit Workload to P2P Network'}
          </button>
        </form>
      </div>
    </div>
  );
};
