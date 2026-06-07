import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Package, UserCheck, RotateCcw, Shield, AlertTriangle,
  CheckCircle, TrendingUp, Clock, Activity
} from 'lucide-react';
import api from '../../services/apiService';
import { SkeletonStat } from '../ui/Skeletons';
import type { DashboardStats, AuditLog } from '../../types';

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const fadeUp = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { duration: 0.5 } } };

interface Props {
  addToast: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

export default function Dashboard({ addToast }: Props) {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsData, logsData] = await Promise.all([
        api.get<DashboardStats>('/assets/stats'),
        api.get<AuditLog[]>('/assets/audit-logs'),
      ]);
      setStats(statsData);
      setLogs(logsData.slice(0, 20));
    } catch {
      addToast('error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <SkeletonStat key={i} />)}
        </div>
      </div>
    );
  }

  const statCards = [
    { label: 'Total Assets', value: stats?.total_assets ?? 0, icon: Package, color: 'from-brand-500 to-cyan-500', glow: 'shadow-brand-500/20' },
    { label: 'Assigned', value: stats?.assigned_assets ?? 0, icon: UserCheck, color: 'from-blue-500 to-indigo-500', glow: 'shadow-blue-500/20' },
    { label: 'Available', value: stats?.available_assets ?? 0, icon: CheckCircle, color: 'from-emerald-500 to-teal-500', glow: 'shadow-emerald-500/20' },
    { label: 'Returned', value: stats?.returned_assets ?? 0, icon: RotateCcw, color: 'from-amber-500 to-yellow-500', glow: 'shadow-amber-500/20' },
    { label: 'Under Audit', value: stats?.under_audit ?? 0, icon: Shield, color: 'from-purple-500 to-violet-500', glow: 'shadow-purple-500/20' },
    { label: 'Pending Clearance', value: stats?.pending_clearance ?? 0, icon: AlertTriangle, color: 'from-orange-500 to-red-500', glow: 'shadow-orange-500/20' },
    { label: 'Cleared', value: stats?.cleared_assets ?? 0, icon: CheckCircle, color: 'from-slate-400 to-slate-500', glow: 'shadow-slate-500/20' },
    { label: 'Categories', value: Object.keys(stats?.categories ?? {}).length, icon: TrendingUp, color: 'from-pink-500 to-rose-500', glow: 'shadow-pink-500/20' },
  ];

  const categoryEntries = Object.entries(stats?.categories ?? {});
  const statusEntries = Object.entries(stats?.status_distribution ?? {});
  const maxStatusCount = Math.max(...statusEntries.map(([, v]) => v), 1);

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 overflow-y-auto h-full">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Real-time overview of your asset inventory</p>
      </motion.div>

      {/* Stat Cards */}
      <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.label}
              variants={fadeUp}
              whileHover={{ y: -4, scale: 1.02 }}
              className={`glass-card-hover p-5 group cursor-default`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{card.label}</span>
                <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center shadow-lg ${card.glow} group-hover:scale-110 transition-transform`}>
                  <Icon className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-white">{card.value}</div>
            </motion.div>
          );
        })}
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Status Distribution */}
        <motion.div variants={fadeUp} initial="hidden" animate="show" className="lg:col-span-2 glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand-400" /> Status Distribution
          </h2>
          {statusEntries.length === 0 ? (
            <p className="text-slate-500 text-sm">No assets tracked yet</p>
          ) : (
            <div className="space-y-4">
              {statusEntries.map(([status, count]) => (
                <div key={status}>
                  <div className="flex justify-between text-sm mb-1.5">
                    <span className="text-slate-300 font-medium">{status}</span>
                    <span className="text-slate-400">{count}</span>
                  </div>
                  <div className="h-2.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(count / maxStatusCount) * 100}%` }}
                      transition={{ duration: 1, delay: 0.3, ease: 'easeOut' }}
                      className="h-full rounded-full bg-gradient-to-r from-brand-500 to-cyan-500"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Categories */}
        <motion.div variants={fadeUp} initial="hidden" animate="show" className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <Package className="w-5 h-5 text-brand-400" /> Categories
          </h2>
          {categoryEntries.length === 0 ? (
            <p className="text-slate-500 text-sm">No categories yet</p>
          ) : (
            <div className="space-y-3">
              {categoryEntries.map(([cat, count]) => (
                <div key={cat} className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                  <span className="text-sm text-slate-300">{cat}</span>
                  <span className="text-sm font-semibold text-brand-400">{count}</span>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Recent Assets & Audit */}
      <div className="grid lg:grid-cols-2 gap-6 mt-6">
        {/* Recent Assets */}
        <motion.div variants={fadeUp} initial="hidden" animate="show" className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <Clock className="w-5 h-5 text-brand-400" /> Recent Assets
          </h2>
          {(stats?.recent_assets ?? []).length === 0 ? (
            <p className="text-slate-500 text-sm">No recent assets</p>
          ) : (
            <div className="space-y-3">
              {stats!.recent_assets.map((asset) => (
                <div key={asset.asset_id} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500/20 to-cyan-500/20 flex items-center justify-center flex-shrink-0">
                    <Package className="w-5 h-5 text-brand-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">
                      {asset.asset_name || asset.asset_type} — {asset.brand}
                    </div>
                    <div className="text-xs text-slate-500">
                      {asset.assigned_to || 'Unassigned'} · {asset.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Audit Activity */}
        <motion.div variants={fadeUp} initial="hidden" animate="show" className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <Shield className="w-5 h-5 text-brand-400" /> Recent Audit Activity
          </h2>
          {logs.length === 0 ? (
            <p className="text-slate-500 text-sm">No audit activity yet</p>
          ) : (
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {logs.slice(0, 8).map((log) => (
                <div key={log.log_id} className="flex items-start gap-3 p-3 rounded-xl bg-white/5">
                  <div className="w-2 h-2 rounded-full bg-brand-400 mt-2 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-slate-300">
                      <span className="font-medium text-white">{log.action}</span> — {log.details}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
