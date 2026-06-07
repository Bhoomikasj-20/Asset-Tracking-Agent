import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Clock, Search, Filter } from 'lucide-react';
import api from '../../services/apiService';
import { SkeletonRow } from '../ui/Skeletons';
import type { AuditLog } from '../../types';

const actionColors: Record<string, string> = {
  Created: 'bg-emerald-500',
  Updated: 'bg-brand-500',
  Assigned: 'bg-blue-500',
  Returned: 'bg-amber-500',
  Cleared: 'bg-slate-400',
  Deleted: 'bg-red-500',
};

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterAction, setFilterAction] = useState('');

  useEffect(() => { loadLogs(); }, []);

  async function loadLogs() {
    try {
      const data = await api.get<AuditLog[]>('/assets/audit-logs');
      setLogs(data);
    } catch {
      // handle silently
    } finally {
      setLoading(false);
    }
  }

  const filtered = logs.filter(log => {
    const matchesSearch = !search || 
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.details.toLowerCase().includes(search.toLowerCase()) ||
      log.asset_id.toLowerCase().includes(search.toLowerCase());
    const matchesAction = !filterAction || log.action === filterAction;
    return matchesSearch && matchesAction;
  });

  const uniqueActions = [...new Set(logs.map(l => l.action))];

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 h-full overflow-y-auto">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">Audit Logs</h1>
        <p className="text-slate-400 text-sm">Complete history of all asset management actions</p>
      </motion.div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search audit logs..."
            className="input-glass w-full pl-10"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <select
            value={filterAction}
            onChange={e => setFilterAction(e.target.value)}
            className="select-glass pl-10 pr-8 min-w-[160px]"
          >
            <option value="">All Actions</option>
            {uniqueActions.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
      </div>

      {/* Logs */}
      {loading ? (
        <div className="glass-card divide-y divide-white/5">
          {[...Array(8)].map((_, i) => <SkeletonRow key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20">
          <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg">No audit logs found</p>
          <p className="text-slate-500 text-sm mt-1">Actions on assets will appear here</p>
        </div>
      ) : (
        <motion.div
          initial="hidden"
          animate="show"
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.03 } } }}
          className="glass-card divide-y divide-white/5"
        >
          {filtered.map(log => (
            <motion.div
              key={log.log_id}
              variants={{ hidden: { opacity: 0, x: -10 }, show: { opacity: 1, x: 0 } }}
              className="flex items-start gap-4 p-4 hover:bg-white/5 transition-colors"
            >
              <div className={`w-2.5 h-2.5 rounded-full mt-2 flex-shrink-0 ${actionColors[log.action] || 'bg-slate-500'}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-white">{log.action}</span>
                  <span className="text-xs text-slate-500">·</span>
                  <span className="text-xs font-mono text-slate-500 truncate">{log.asset_id.slice(0, 12)}...</span>
                </div>
                <p className="text-sm text-slate-400 mt-0.5">{log.details}</p>
                <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                  <span>by {log.performed_by}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}
