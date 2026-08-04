import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus, Search, Package, Pencil, Trash2, UserCheck, RotateCcw,
  CheckCircle, X, Filter, Loader2
} from 'lucide-react';
import api from '../../services/apiService';
import { SkeletonCard } from '../ui/Skeletons';
import type { Asset } from '../../types';

interface Props {
  addToast: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

const STATUS_OPTIONS = ['Available', 'Assigned', 'Returned', 'Under Audit', 'Pending Clearance', 'Cleared', 'Active', 'In Repair', 'Disposed'];
const CATEGORY_OPTIONS = ['General', 'Laptop', 'Desktop', 'Mobile', 'Server', 'Monitor', 'Printer', 'Network', 'Accessory', 'Software', 'Other'];

const emptyAsset = {
  asset_name: '', asset_type: '', category: 'General', brand: '', model_number: '',
  assigned_to: '', purchase_date: '', warranty_expiry: '', location: '', notes: '', status: 'Available',
};

function getStatusClass(status: string) {
  const s = (status || '').toLowerCase().replace(/\s+/g, '-');
  return `status-badge status-${s}`;
}

export default function AssetManager({ addToast }: Props) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ ...emptyAsset });
  const [saving, setSaving] = useState(false);

  useEffect(() => { loadAssets(); }, []);

  async function loadAssets() {
    setLoading(true);
    try {
      const data = await api.get<Asset[]>('/assets');
      setAssets(data);
    } catch {
      addToast('error', 'Failed to load assets');
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) { loadAssets(); return; }
    try {
      const data = await api.get<Asset[]>('/assets/search', { q: searchQuery });
      setAssets(data);
    } catch {
      addToast('error', 'Search failed');
    }
  }

  async function handleFilterStatus(status: string) {
    setFilterStatus(status);
    if (!status) { loadAssets(); return; }
    try {
      const data = await api.get<Asset[]>(`/assets/status/${status}`);
      setAssets(data);
    } catch {
      addToast('error', 'Filter failed');
    }
  }

  function openCreateModal() {
    setForm({ ...emptyAsset });
    setEditingId(null);
    setModalOpen(true);
  }

  function openEditModal(asset: Asset) {
    setForm({
      asset_name: asset.asset_name || '',
      asset_type: asset.asset_type || '',
      category: asset.category || 'General',
      brand: asset.brand || '',
      model_number: asset.model_number || '',
      assigned_to: asset.assigned_to || '',
      purchase_date: asset.purchase_date || '',
      warranty_expiry: asset.warranty_expiry || '',
      location: asset.location || '',
      notes: asset.notes || '',
      status: asset.status || 'Available',
    });
    setEditingId(asset.asset_id);
    setModalOpen(true);
  }

  async function handleSave() {
    if (!form.asset_type || !form.brand) {
      addToast('warning', 'Asset type and brand are required');
      return;
    }
    setSaving(true);
    try {
      if (editingId) {
        await api.put(`/assets/${editingId}`, form);
        addToast('success', 'Asset updated successfully');
      } else {
        await api.post('/assets', form);
        addToast('success', 'Asset created successfully');
      }
      setModalOpen(false);
      loadAssets();
    } catch {
      addToast('error', 'Failed to save asset');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await api.del(`/assets/${id}`);
      addToast('success', 'Asset deleted');
      loadAssets();
    } catch {
      addToast('error', 'Failed to delete asset');
    }
  }

  async function handleAssign(id: string) {
    const employee = prompt('Enter employee name:');
    if (!employee) return;
    try {
      await api.put(`/assets/${id}/assign`, { employee });
      addToast('success', `Asset assigned to ${employee}`);
      loadAssets();
    } catch {
      addToast('error', 'Failed to assign asset');
    }
  }

  async function handleReturn(id: string) {
    try {
      await api.put(`/assets/${id}/return`, {});
      addToast('success', 'Asset marked as returned');
      loadAssets();
    } catch {
      addToast('error', 'Failed to return asset');
    }
  }

  async function handleClearance(id: string) {
    try {
      await api.put(`/assets/${id}/clearance`, {});
      addToast('success', 'Asset cleared');
      loadAssets();
    } catch {
      addToast('error', 'Failed to clear asset');
    }
  }

  const filtered = filterStatus
    ? assets.filter(a => a.status?.toLowerCase() === filterStatus.toLowerCase())
    : assets;

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 h-full overflow-y-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-1">Asset Management</h1>
          <p className="text-slate-400 text-sm">{assets.length} assets in inventory</p>
        </div>
        <button onClick={openCreateModal} className="btn-primary flex items-center gap-2 text-sm self-start">
          <Plus className="w-4 h-4" /> Add Asset
        </button>
      </motion.div>

      {/* Search & Filter */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Search assets by name, type, brand, employee..."
            className="input-glass w-full pl-10"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <select
            value={filterStatus}
            onChange={e => handleFilterStatus(e.target.value)}
            className="select-glass pl-10 pr-8 min-w-[180px]"
          >
            <option value="">All Statuses</option>
            {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </motion.div>

      {/* Asset Grid */}
      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20">
          <Package className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg mb-2">No assets found</p>
          <p className="text-slate-500 text-sm mb-6">Add your first asset to get started</p>
          <button onClick={openCreateModal} className="btn-primary text-sm">
            <Plus className="w-4 h-4 inline mr-2" /> Create Asset
          </button>
        </div>
      ) : (
        <motion.div
          initial="hidden"
          animate="show"
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {filtered.map((asset) => (
            <motion.div
              key={asset.asset_id}
              variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
              whileHover={{ y: -3 }}
              className="glass-card-hover p-5 group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-white truncate">
                    {asset.asset_name || asset.asset_type}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">{asset.brand} · {asset.model_number}</p>
                </div>
                <span className={getStatusClass(asset.status)}>{asset.status}</span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-400 mb-4">
                <div className="flex justify-between">
                  <span>Category</span>
                  <span className="text-slate-300">{asset.category || 'General'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Assigned To</span>
                  <span className="text-slate-300">{asset.assigned_to || '—'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Purchase Date</span>
                  <span className="text-slate-300">{asset.purchase_date || '—'}</span>
                </div>
                {asset.location && (
                  <div className="flex justify-between">
                    <span>Location</span>
                    <span className="text-slate-300">{asset.location}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-1.5 pt-3 border-t border-white/5">
                <button onClick={() => openEditModal(asset)} title="Edit" className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-brand-400 transition-all">
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => handleAssign(asset.asset_id)} title="Assign" className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-blue-400 transition-all">
                  <UserCheck className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => handleReturn(asset.asset_id)} title="Return" className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-amber-400 transition-all">
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => handleClearance(asset.asset_id)} title="Clear" className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-emerald-400 transition-all">
                  <CheckCircle className="w-3.5 h-3.5" />
                </button>
                <div className="flex-1" />
                <button onClick={() => handleDelete(asset.asset_id)} title="Delete" className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-500 hover:text-red-400 transition-all">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Modal */}
      <AnimatePresence>
        {modalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={() => setModalOpen(false)}
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              className="relative glass-card border-white/10 p-6 w-full max-w-lg max-h-[85vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-white">
                  {editingId ? 'Edit Asset' : 'Add New Asset'}
                </h2>
                <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Asset Name</label>
                  <input value={form.asset_name} onChange={e => setForm(f => ({ ...f, asset_name: e.target.value }))} className="input-glass w-full" placeholder="e.g. MacBook Pro 16" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Asset Type *</label>
                  <input value={form.asset_type} onChange={e => setForm(f => ({ ...f, asset_type: e.target.value }))} className="input-glass w-full" placeholder="e.g. Laptop" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Category</label>
                  <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} className="select-glass w-full">
                    {CATEGORY_OPTIONS.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Brand *</label>
                  <input value={form.brand} onChange={e => setForm(f => ({ ...f, brand: e.target.value }))} className="input-glass w-full" placeholder="e.g. Apple" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Model Number</label>
                  <input value={form.model_number} onChange={e => setForm(f => ({ ...f, model_number: e.target.value }))} className="input-glass w-full" placeholder="e.g. A2485" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Assigned To</label>
                  <input value={form.assigned_to} onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))} className="input-glass w-full" placeholder="Employee name" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="select-glass w-full">
                    {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Purchase Date</label>
                  <input type="date" value={form.purchase_date} onChange={e => setForm(f => ({ ...f, purchase_date: e.target.value }))} className="input-glass w-full" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Warranty Expiry</label>
                  <input type="date" value={form.warranty_expiry} onChange={e => setForm(f => ({ ...f, warranty_expiry: e.target.value }))} className="input-glass w-full" />
                </div>
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Location</label>
                  <input value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))} className="input-glass w-full" placeholder="e.g. Building A, Floor 3" />
                </div>
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">Notes</label>
                  <textarea value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} rows={2} className="input-glass w-full resize-none" placeholder="Additional notes..." />
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-white/5">
                <button onClick={() => setModalOpen(false)} className="btn-secondary text-sm px-5">Cancel</button>
                <button onClick={handleSave} disabled={saving} className="btn-primary text-sm px-5 flex items-center gap-2">
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {editingId ? 'Update Asset' : 'Create Asset'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
