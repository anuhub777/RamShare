import React, { useEffect, useState } from 'react';
import { creditsApi } from '../api/credits';
import { StatCard } from '../components/common/StatCard';
import { CreditChart } from '../components/charts/CreditChart';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Coins, ArrowDownLeft, ArrowUpRight, Gift } from 'lucide-react';

export const CreditWalletPage = () => {
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWallet = async () => {
      try {
        const [balRes, txnRes] = await Promise.all([
          creditsApi.getBalance(),
          creditsApi.getTransactions()
        ]);
        setBalance(balRes.data.balance);
        setTransactions(txnRes.data.transactions || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchWallet();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Credit Wallet & Ledger</h1>
        <p className="text-sm text-slate-400">Transparent credit economy balance & atomic transaction history.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Available Balance" value={`${balance.toFixed(1)} cr`} subtitle="Active spending power" icon={Coins} color="amber" />
        <StatCard
          title="Total Earned"
          value={`${transactions.filter(t => t.transaction_type === 'EARNING').reduce((acc, t) => acc + t.amount, 0).toFixed(1)} cr`}
          subtitle="Provider workload rewards"
          icon={ArrowDownLeft}
          color="emerald"
        />
        <StatCard
          title="Total Spent"
          value={`${transactions.filter(t => t.transaction_type === 'SPENDING').reduce((acc, t) => acc + t.amount, 0).toFixed(1)} cr`}
          subtitle="Consumer compute jobs"
          icon={ArrowUpRight}
          color="blue"
        />
      </div>

      <div className="card">
        <h2 className="font-bold text-white mb-4">Earnings vs Spend Trend</h2>
        <CreditChart />
      </div>

      <div className="card">
        <h2 className="text-lg font-bold text-white mb-4">Transaction History</h2>
        {loading ? (
          <LoadingSpinner label="Loading ledger..." />
        ) : transactions.length === 0 ? (
          <p className="text-sm text-slate-400 py-6 text-center">No credit transactions recorded yet.</p>
        ) : (
          <div className="divide-y divide-slate-800">
            {transactions.map((t) => (
              <div key={t.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-white text-sm">{t.description}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                      t.transaction_type === 'EARNING' || t.transaction_type === 'SIGNUP_BONUS'
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'bg-red-500/10 text-red-400'
                    }`}>
                      {t.transaction_type}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500">{new Date(t.created_at).toLocaleString()}</span>
                </div>

                <div className="text-right">
                  <span className={`font-bold text-sm ${
                    t.transaction_type === 'SPENDING' ? 'text-red-400' : 'text-emerald-400'
                  }`}>
                    {t.transaction_type === 'SPENDING' ? '-' : '+'}{t.amount.toFixed(1)} cr
                  </span>
                  <div className="text-xs text-slate-500">Balance: {t.balance_after.toFixed(1)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
