import React from 'react';
import { Link } from 'react-router-dom';
import { Cpu, ShieldCheck, Zap, Coins, Globe, ArrowRight, Server, Terminal } from 'lucide-react';

export const LandingPage = () => {
  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 flex flex-col">
      {/* Top Banner */}
      <header className="border-b border-slate-800/80 bg-navy-950/70 backdrop-blur sticky top-0 z-30 px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600/20 border border-blue-500/30 p-1.5 rounded-lg text-blue-500">
            <Cpu className="h-6 w-6" />
          </div>
          <span className="text-xl font-bold tracking-tight">RAM<span className="text-blue-500">Share</span></span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-secondary text-sm">Sign In</Link>
          <Link to="/register" className="btn-primary text-sm">Join Marketplace</Link>
        </div>
      </header>

      {/* Hero */}
      <section className="relative px-6 py-24 text-center max-w-5xl mx-auto flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-6">
          <Zap className="h-3.5 w-3.5" /> Peer-to-Peer Computing Economy
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Decentralized Cloud Computing <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400">
            Powered by Millions of PCs
          </span>
        </h1>
        <p className="mt-6 text-lg text-slate-400 max-w-2xl">
          Monetize your unused CPU and RAM capacity as a Provider. Run scalable data processing, benchmarks, and ML inference at a fraction of cloud costs as a Consumer.
        </p>

        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          <Link to="/register" className="btn-primary flex items-center gap-2 text-base px-6 py-3">
            Start Computing Now <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/marketplace" className="btn-secondary flex items-center gap-2 text-base px-6 py-3">
            Explore Available Nodes
          </Link>
        </div>

        {/* Live Metrics Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-16 w-full max-w-4xl pt-8 border-t border-slate-800/80">
          <div>
            <div className="text-2xl font-bold text-white">100%</div>
            <div className="text-xs text-slate-400 uppercase mt-1">Docker Isolated</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-400">90%</div>
            <div className="text-xs text-slate-400 uppercase mt-1">Cost Savings</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-400">&lt; 15s</div>
            <div className="text-xs text-slate-400 uppercase mt-1">Matchmaking</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-cyan-400">Zero</div>
            <div className="text-xs text-slate-400 uppercase mt-1">AWS Host Overhead</div>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="px-6 py-16 bg-navy-900/40 border-y border-slate-800/60">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">How RAMShare Works</h2>
            <p className="text-slate-400 text-sm mt-2">AWS handles orchestration; computation executes on provider machines.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="card">
              <div className="h-10 w-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-4">
                <Terminal className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg text-white mb-2">1. Lightweight Desktop Agent</h3>
              <p className="text-sm text-slate-400">
                Providers run a terminal agent that monitors CPU & RAM using psutil and enforces provider limits.
              </p>
            </div>

            <div className="card">
              <div className="h-10 w-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mb-4">
                <Zap className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg text-white mb-2">2. Intelligent Matchmaking</h3>
              <p className="text-sm text-slate-400">
                Algorithms match consumer workloads to the most capable online provider based on memory, CPU, and reliability.
              </p>
            </div>

            <div className="card">
              <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <Coins className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-lg text-white mb-2">3. Internal Credit Economy</h3>
              <p className="text-sm text-slate-400">
                Consumers spend credits; providers receive rewards automatically upon successful verified Docker execution.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800 px-6 py-6 text-center text-xs text-slate-400">
        &copy; {new Date().getFullYear()} RAMShare Marketplace. All rights reserved.
      </footer>
    </div>
  );
};
