import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Cpu, LogOut, User as UserIcon, Coins } from 'lucide-react';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-navy-950/80 backdrop-blur">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="rounded-lg bg-blue-600/20 p-2 text-blue-500 border border-blue-500/30">
            <Cpu className="h-6 w-6" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">RAM<span className="text-blue-500">Share</span></span>
        </Link>

        {isAuthenticated ? (
          <div className="flex items-center gap-4">
            <Link to="/credits" className="flex items-center gap-2 rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-sm font-medium text-amber-400 hover:border-slate-700 transition">
              <Coins className="h-4 w-4" />
              <span>{user?.credit_balance?.toFixed(1) || 0} Credits</span>
            </Link>

            <Link to="/profile" className="flex items-center gap-2 text-sm text-slate-300 hover:text-white transition">
              <div className="h-8 w-8 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center font-bold text-blue-400">
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </div>
              <span className="hidden md:inline">{user?.username}</span>
            </Link>

            <button
              onClick={() => { logout(); navigate('/login'); }}
              className="text-slate-400 hover:text-red-400 transition p-1.5"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm">Sign In</Link>
            <Link to="/register" className="btn-primary text-sm">Get Started</Link>
          </div>
        )}
      </div>
    </header>
  );
};
