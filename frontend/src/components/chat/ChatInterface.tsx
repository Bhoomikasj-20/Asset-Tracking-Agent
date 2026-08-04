import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Plus, Trash2, MessageSquare, Bot, User,
  Zap, ChevronRight, Loader2, Cpu
} from 'lucide-react';
import { marked } from 'marked';
import api from '../../services/apiService';
import type { Session, ChatPart } from '../../types';

const AGENT_NAME = 'agent';

interface DisplayMessage {
  id: string;
  role: 'user' | 'model' | 'function';
  parts: ChatPart[];
  timestamp: Date;
}

interface Props {
  addToast: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

export default function ChatInterface({ addToast }: Props) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState('');
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function loadSessions() {
    try {
      const data = await api.get<Session[]>(`/apps/${AGENT_NAME}/users/user/sessions`);
      setSessions(Array.isArray(data) ? data : []);
      if (Array.isArray(data) && data.length > 0) {
        selectSession(data[0].id);
      }
    } catch (err) {
      console.warn('Could not load sessions:', err);
    }
  }

  async function selectSession(id: string) {
    setActiveSession(id);
    setMessages([]);
    try {
      const session = await api.get<{ events?: Array<{ content?: { role: string; parts: ChatPart[] } }> }>(
        `/apps/${AGENT_NAME}/users/user/sessions/${id}`
      );
      if (session.events && Array.isArray(session.events)) {
        const msgs: DisplayMessage[] = [];
        session.events.forEach((evt, idx) => {
          if (evt.content?.parts && Array.isArray(evt.content.parts)) {
            // Skip internal messages when loading history
            if ((evt.content as any).metadata?.internal) return;
            
            const role = evt.content.role === 'user' ? 'user' :
              evt.content.parts.some(p => p.functionCall || p.functionResponse) ? 'function' : 'model';
            
            // Further filter if role became function but we want it hidden
            if (role === 'function') return;

            msgs.push({
              id: `${id}-${idx}`,
              role: role as any,
              parts: evt.content.parts,
              timestamp: new Date(),
            });
          }
        });
        setMessages(msgs);
      }
    } catch (err) {
      console.error('Failed to load session:', err);
      addToast('error', 'Failed to load session');
    }
  }

  async function createSession() {
    try {
      const session = await api.post<Session>(`/apps/${AGENT_NAME}/users/user/sessions`);
      if (session?.id) {
        setSessions(prev => [session, ...prev]);
        selectSession(session.id);
        addToast('success', 'New session created');
      }
    } catch (err) {
      console.error('Failed to create session:', err);
      addToast('error', 'Failed to create session. Make sure the backend is running.');
    }
  }

  async function deleteSession(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    try {
      await api.del(`/apps/${AGENT_NAME}/users/user/sessions/${id}`);
      setSessions(prev => prev.filter(s => s.id !== id));
      if (activeSession === id) {
        setMessages([]);
        setActiveSession('');
      }
      addToast('info', 'Session deleted');
    } catch {
      addToast('error', 'Failed to delete session');
    }
  }

  async function sendMessage() {
    if (!input.trim() || sending) return;
    if (!activeSession) {
      addToast('warning', 'Please create a session first');
      return;
    }

    const text = input.trim();
    setInput('');
    setSending(true);

    const userMsg: DisplayMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      parts: [{ text }],
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    const payload = {
      appName: AGENT_NAME,
      newMessage: { role: 'user', parts: [{ text }] },
      sessionId: activeSession,
      stateDelta: null,
      streaming: false,
      userId: 'user',
    };

    let gotResponse = false;

    try {
      const apiBase = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiBase}/run_sse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream, application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errText = await response.text().catch(() => '');
        throw new Error(`Server error ${response.status}: ${errText.slice(0, 200)}`);
      }

      if (!response.body) {
        // Fallback: try reading as JSON
        const json = await response.json();
        if (json?.content?.parts) {
          gotResponse = true;
          addResponseMessage(json);
        }
      } else {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            // Process remaining buffer
            if (buffer.trim()) {
              processSSELines(buffer, (data) => {
                gotResponse = true;
                addResponseMessage(data);
              });
            }
            break;
          }

          buffer += decoder.decode(value, { stream: true });

          // Process complete lines
          let newlineIndex: number;
          while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
            const line = buffer.slice(0, newlineIndex).trim();
            buffer = buffer.slice(newlineIndex + 1);
            if (!line) continue;

            processSSELines(line, (data) => {
              gotResponse = true;
              addResponseMessage(data);
            });
          }
        }
      }

      if (!gotResponse) {
        const noResponseMsg: DisplayMessage = {
          id: `empty-${Date.now()}`,
          role: 'model',
          parts: [{ text: 'AI assistant temporarily unavailable' }],
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, noResponseMsg]);
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      addToast('error', `Chat error: ${errorMessage.slice(0, 100)}`);
      const errorMsg: DisplayMessage = {
        id: `err-${Date.now()}`,
        role: 'model',
        parts: [{
          text: 'AI assistant temporarily unavailable'
        }],
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }

  function processSSELines(text: string, onData: (data: unknown) => void) {
    // Handle multiple SSE formats
    const lines = text.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      let jsonStr = trimmed;
      // Strip SSE "data:" prefix
      if (jsonStr.startsWith('data:')) {
        jsonStr = jsonStr.slice(5).trim();
      }
      // Skip SSE control lines
      if (jsonStr.startsWith('event:') || jsonStr.startsWith('id:') || jsonStr.startsWith('retry:')) {
        continue;
      }
      if (jsonStr === '[DONE]') continue;

      try {
        const parsed = JSON.parse(jsonStr);
        onData(parsed);
      } catch {
        // Not valid JSON, skip
      }
    }
  }

  function addResponseMessage(data: unknown) {
    const d = data as Record<string, unknown>;

    // Check for ADK error events
    if (d?.error || d?.errorMessage || d?.status === 'error') {
      const msg: DisplayMessage = {
        id: `err-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        role: 'model',
        parts: [{ text: 'AI assistant temporarily unavailable' }],
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, msg]);
      return;
    }

    const content = d?.content as { role?: string; parts?: ChatPart[]; metadata?: { internal?: boolean } } | undefined;

    if (content?.parts && Array.isArray(content.parts) && content.parts.length > 0) {
      // Skip user echo
      if (content.role === 'user') return;

      // Skip internal tool execution messages
      if (content.metadata?.internal) return;

      // Ensure we don't show function results directly
      if (content.role === 'function') return;
      if (content.parts.some(p => p.functionCall || p.functionResponse)) return;

      const msg: DisplayMessage = {
        id: `resp-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        role: 'model',
        parts: content.parts,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, msg]);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="flex h-full overflow-hidden">
      {/* Sessions Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="h-full border-r border-white/5 bg-surface-950/50 backdrop-blur-xl flex flex-col overflow-hidden flex-shrink-0"
          >
            <div className="p-4 border-b border-white/5">
              <button onClick={createSession} className="btn-primary w-full flex items-center justify-center gap-2 text-sm py-2.5">
                <Plus className="w-4 h-4" /> New Session
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-1">
              {sessions.length === 0 && (
                <div className="text-center py-8 text-slate-500 text-sm">
                  <MessageSquare className="w-8 h-8 mx-auto mb-3 opacity-30" />
                  No sessions yet
                </div>
              )}
              {sessions.map(session => (
                <motion.button
                  key={session.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  onClick={() => selectSession(session.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left text-sm transition-all group
                    ${activeSession === session.id
                      ? 'bg-brand-600/20 text-brand-400 border border-brand-500/20'
                      : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'}`}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <span className="flex-1 truncate font-mono text-xs">{session.id.slice(0, 16)}...</span>
                  <button
                    onClick={(e) => deleteSession(e, session.id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all p-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </motion.button>
              ))}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Chat Header */}
        <div className="flex items-center gap-3 px-4 sm:px-6 py-3 border-b border-white/5 bg-surface-950/30 backdrop-blur-sm">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-all">
            <ChevronRight className={`w-4 h-4 transition-transform ${sidebarOpen ? 'rotate-180' : ''}`} />
          </button>
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500 to-cyan-500 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">AssetsTracking Agent</h2>
            <p className="text-xs text-slate-500">AI-powered asset management assistant</p>
          </div>
          {sending && (
            <div className="ml-auto flex items-center gap-2 text-xs text-brand-400">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing...
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4">
          {messages.length === 0 && !sending && (
            <div className="flex flex-col items-center justify-center h-full text-center py-16">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-brand-500/20 to-cyan-500/20 flex items-center justify-center mb-6 animate-float">
                <Bot className="w-10 h-10 text-brand-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">AssetsTracking Agent</h3>
              <p className="text-slate-400 text-sm max-w-md mb-8">
                Your intelligent assistant for asset management. Ask me to assign laptops, track equipment, run audits, or manage clearances.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
                {[
                  'Show all available assets',
                  'Assign laptop to Ravi',
                  'Generate audit summary',
                  'How many assets are active?',
                ].map(suggestion => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      setInput(suggestion);
                      inputRef.current?.focus();
                    }}
                    className="text-left px-4 py-3 rounded-xl bg-white/5 border border-white/5 text-sm text-slate-400 hover:text-white hover:bg-white/10 hover:border-white/10 transition-all group"
                  >
                    <Zap className="w-3.5 h-3.5 inline mr-2 text-brand-500 group-hover:text-brand-400" />
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role !== 'user' && (
                  <div className={`w-8 h-8 rounded-xl flex-shrink-0 overflow-hidden mt-1 shadow-lg ring-1 ring-white/10
                    ${msg.role === 'function' ? 'bg-purple-500/20' : ''}`}>
                    {msg.role === 'function' ? (
                      <div className="w-full h-full flex items-center justify-center">
                        <Zap className="w-4 h-4 text-purple-400" />
                      </div>
                    ) : (
                      <img src="/avatar.png" alt="AI" className="w-full h-full object-cover" />
                    )}
                  </div>
                )}

                <div className={`max-w-[75%]`}>
                  {msg.parts.map((part, idx) => {
                    if (part.text) {
                      return (
                        <div
                          key={idx}
                          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
                            ${msg.role === 'user'
                              ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white rounded-br-md'
                              : 'bg-white/5 border border-white/5 text-slate-200 rounded-bl-md'}`}
                        >
                          {msg.role === 'user' ? (
                            <span>{part.text}</span>
                          ) : (
                            <div
                              className="chat-markdown"
                              dangerouslySetInnerHTML={{ __html: marked.parse(part.text) as string }}
                            />
                          )}
                        </div>
                      );
                    }
                    return null;
                  })}
                  <div className={`text-[10px] mt-1 ${msg.role === 'user' ? 'text-right' : 'text-left'} text-slate-600`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex-shrink-0 flex items-center justify-center mt-1">
                    <User className="w-4 h-4 text-emerald-400" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {sending && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
              <div className="w-8 h-8 rounded-xl overflow-hidden flex-shrink-0 shadow-lg ring-1 ring-white/10">
                <img src="/avatar.png" alt="AI" className="w-full h-full object-cover" />
              </div>
              <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-white/5 border border-white/5">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-brand-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-brand-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-brand-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-white/5 bg-surface-950/30 backdrop-blur-sm p-4">
          <div className="max-w-4xl mx-auto flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={activeSession ? 'Ask about your assets...' : 'Create a session to start chatting'}
                disabled={sending || !activeSession}
                rows={1}
                className="input-glass w-full pr-4 resize-none min-h-[48px] max-h-[120px]"
                style={{ height: 'auto' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={sending || !input.trim() || !activeSession}
              className="btn-primary p-3 rounded-xl disabled:opacity-30"
            >
              {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
