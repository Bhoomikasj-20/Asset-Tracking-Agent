import { useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import LandingPage from './pages/LandingPage';
import Dashboard from './components/dashboard/Dashboard';
import ChatInterface from './components/chat/ChatInterface';
import AssetManager from './components/assets/AssetManager';
import AuditLogs from './components/audit/AuditLogs';
import ToastContainer from './components/ui/ToastContainer';
import type { ToastMessage } from './types';

export default function App() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback((type: ToastMessage['type'], message: string) => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-surface-950 text-white">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route
            path="/*"
            element={
              <div className="flex flex-col h-screen">
                <Navbar />
                <main className="flex-1 overflow-hidden">
                  <Routes>
                    <Route path="/dashboard" element={<Dashboard addToast={addToast} />} />
                    <Route path="/chat" element={<ChatInterface addToast={addToast} />} />
                    <Route path="/assets" element={<AssetManager addToast={addToast} />} />
                    <Route path="/audit" element={<AuditLogs />} />
                  </Routes>
                </main>
              </div>
            }
          />
        </Routes>
        <ToastContainer toasts={toasts} removeToast={removeToast} />
      </div>
    </BrowserRouter>
  );
}
