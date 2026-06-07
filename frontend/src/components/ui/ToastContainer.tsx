import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';
import type { ToastMessage } from '../../types';

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

const colors = {
  success: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30 text-emerald-400',
  error: 'from-red-500/20 to-red-500/5 border-red-500/30 text-red-400',
  info: 'from-brand-500/20 to-brand-500/5 border-brand-500/30 text-brand-400',
  warning: 'from-amber-500/20 to-amber-500/5 border-amber-500/30 text-amber-400',
};

interface Props {
  toasts: ToastMessage[];
  removeToast: (id: string) => void;
}

export default function ToastContainer({ toasts, removeToast }: Props) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
      <AnimatePresence>
        {toasts.map(toast => {
          const Icon = icons[toast.type];
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 30, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className={`flex items-center gap-3 px-5 py-3.5 rounded-xl border backdrop-blur-xl bg-gradient-to-r ${colors[toast.type]} shadow-lg min-w-[300px] max-w-[420px]`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium flex-1">{toast.message}</span>
              <button onClick={() => removeToast(toast.id)} className="text-white/40 hover:text-white transition-colors">
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
