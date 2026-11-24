import React, { useEffect, useState } from 'react';
import { marketplaceApi } from '../api/marketplace';
import { ProviderCard } from '../components/provider/ProviderCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Layers, Search, Filter } from 'lucide-react';

export const MarketplacePage = () => {
  const [resources, setResources] = useState([]);
  const [filterOs, setFilterOs] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchResources = async () => {
      try {
        const res = await marketplaceApi.getResources();
        if (isMounted) setResources(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchResources();
    const interval = setInterval(fetchResources, 5000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const filtered = resources.filter((r) => {
    const matchesOs = filterOs === 'ALL' || r.os_type?.toUpperCase() === filterOs;
    const matchesSearch = !searchTerm || r.machine_name?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesOs && matchesSearch;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Resource Marketplace</h1>
        <p className="text-sm text-slate-400">Discover active distributed nodes ready to execute your workloads.</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search provider nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-slate-800 bg-navy-900 pl-10 pr-4 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
          />
        </div>
        <select
          value={filterOs}
          onChange={(e) => setFilterOs(e.target.value)}
          className="rounded-lg border border-slate-800 bg-navy-900 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
        >
          <option value="ALL">All Operating Systems</option>
          <option value="LINUX">Linux</option>
          <option value="DARWIN">macOS (Darwin)</option>
          <option value="WINDOWS">Windows</option>
        </select>
      </div>

      {loading ? (
        <LoadingSpinner label="Fetching active peer nodes..." />
      ) : filtered.length === 0 ? (
        <div className="card text-center py-12 text-slate-400">
          <Layers className="h-10 w-10 mx-auto text-slate-600 mb-2" />
          <p className="font-semibold text-slate-300">No active nodes match the criteria</p>
          <p className="text-xs text-slate-500 mt-1">Start a provider agent locally to see it immediately appear here in real-time!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((p) => (
            <ProviderCard key={p.provider_id || p.id} provider={p} />
          ))}
        </div>
      )}
    </div>
  );
};
