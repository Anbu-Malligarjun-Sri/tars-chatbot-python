import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock, Trash2, Edit2, MessageSquare, Plus, Check, Download } from 'lucide-react';
import { useState } from 'react';
import { useTarsStore } from '@/store/tarsStore';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

export function ChatHistory() {
  const { 
    sessions, 
    currentSessionId, 
    isHistoryOpen,
    setHistoryOpen,
    loadSession,
    deleteSession,
    renameSession,
    createNewSession,
    exportAllSessions
  } = useTarsStore();
  
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');

  const handleStartEdit = (id: string, currentName: string) => {
    setEditingId(id);
    setEditName(currentName);
  };

  const handleSaveEdit = (id: string) => {
    if (editName.trim()) {
      renameSession(id, editName.trim());
    }
    setEditingId(null);
  };

  const handleExport = () => {
    const data = exportAllSessions();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tars-sessions-${format(new Date(), 'yyyy-MM-dd')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AnimatePresence>
      {isHistoryOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setHistoryOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />
          
          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className={cn(
              "fixed right-0 top-0 bottom-0 w-80 z-50",
              "bg-tars-dark border-l border-border",
              "flex flex-col overflow-hidden"
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-tars-amber" />
                <span className="font-terminal text-xs uppercase tracking-widest text-tars-light">
                  Mission Logs
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleExport}
                  className="p-2 hover:bg-tars-silver rounded transition-colors text-muted-foreground hover:text-tars-light"
                  title="Export all sessions"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setHistoryOpen(false)}
                  className="p-2 hover:bg-tars-silver rounded transition-colors text-muted-foreground hover:text-tars-light"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            {/* New Session Button */}
            <div className="p-3 border-b border-border">
              <button
                onClick={() => {
                  createNewSession();
                  setHistoryOpen(false);
                }}
                className={cn(
                  "w-full flex items-center justify-center gap-2 p-3 rounded",
                  "bg-tars-silver/50 border border-dashed border-border",
                  "hover:border-tars-amber/50 hover:bg-tars-silver",
                  "transition-all duration-200 mechanical-click",
                  "font-terminal text-[10px] uppercase tracking-wider text-muted-foreground hover:text-tars-light"
                )}
              >
                <Plus className="w-4 h-4" />
                New Session
              </button>
            </div>
            
            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {sessions.length === 0 ? (
                <div className="text-center py-8">
                  <MessageSquare className="w-8 h-8 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="font-terminal text-xs text-muted-foreground/50">
                    No mission logs recorded
                  </p>
                </div>
              ) : (
                sessions.map((session) => (
                  <motion.div
                    key={session.id}
                    layout
                    className={cn(
                      "group relative p-3 rounded border transition-all duration-200",
                      currentSessionId === session.id
                        ? "bg-tars-silver border-tars-amber/30"
                        : "bg-tars-dark/50 border-border hover:border-tars-amber/20 hover:bg-tars-silver/30"
                    )}
                  >
                    {editingId === session.id ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={editName}
                          onChange={(e) => setEditName(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit(session.id)}
                          className="flex-1 bg-tars-dark border border-tars-amber/30 rounded px-2 py-1 font-terminal text-xs text-tars-light focus:outline-none focus:border-tars-amber"
                          autoFocus
                        />
                        <button
                          onClick={() => handleSaveEdit(session.id)}
                          className="p-1 hover:bg-tars-amber/20 rounded"
                        >
                          <Check className="w-3.5 h-3.5 text-tars-green" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => loadSession(session.id)}
                          className="w-full text-left"
                        >
                          <h4 className="font-terminal text-xs text-tars-light truncate mb-1">
                            {session.name}
                          </h4>
                          <div className="flex items-center gap-3 text-[10px] text-muted-foreground/60 font-terminal">
                            <span>{session.messages.length} msgs</span>
                            <span>•</span>
                            <span>{format(new Date(session.updatedAt), 'MMM d, HH:mm')}</span>
                          </div>
                        </button>
                        
                        {/* Actions */}
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => handleStartEdit(session.id, session.name)}
                            className="p-1.5 hover:bg-tars-amber/20 rounded transition-colors"
                          >
                            <Edit2 className="w-3 h-3 text-muted-foreground hover:text-tars-light" />
                          </button>
                          <button
                            onClick={() => deleteSession(session.id)}
                            className="p-1.5 hover:bg-tars-red/20 rounded transition-colors"
                          >
                            <Trash2 className="w-3 h-3 text-muted-foreground hover:text-tars-red" />
                          </button>
                        </div>
                      </>
                    )}
                  </motion.div>
                ))
              )}
            </div>
            
            {/* Footer Stats */}
            <div className="p-3 border-t border-border bg-tars-dark/50">
              <div className="flex items-center justify-between font-terminal text-[10px] text-muted-foreground/50">
                <span>{sessions.length} total sessions</span>
                <span>{sessions.reduce((acc, s) => acc + s.messages.length, 0)} messages</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
