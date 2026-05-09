'use client';

import { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';
import { backendApi } from '../lib/backend/client';
import type { ChatSession } from '../lib/backend/types';

interface ChatContextType {
  sessions: ChatSession[];
  currentSessionId: string | null;
  setCurrentSessionId: (id: string | null) => void;
  createNewSession: () => Promise<void>;
  deleteSession: (id: string) => Promise<void>;
  refreshSessions: () => Promise<ChatSession[]>;
  updateSessionTitle: (id: string, title: string) => void;
  isLoadingSessions: boolean;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const isInitializing = useRef(false);

  const refreshSessions = async () => {
    try {
      const fetched = await backendApi.listChatSessions();
      setSessions(fetched);
      return fetched;
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      return [];
    }
  };

  const createNewSession = async () => {
    try {
      const session = await backendApi.createChatSession({ title: null });
      setSessions((prev) => [session, ...prev]);
      setCurrentSessionId(session.id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const deleteSession = async (id: string) => {
    try {
      await backendApi.deleteChatSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (currentSessionId === id) {
        const remaining = sessions.filter((s) => s.id !== id);
        setCurrentSessionId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const updateSessionTitle = (id: string, title: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, title } : s))
    );
  };

  useEffect(() => {
    const init = async () => {
      if (isInitializing.current) return;
      isInitializing.current = true;
      
      setIsLoadingSessions(true);
      const fetched = await refreshSessions();
      if (fetched.length > 0 && !currentSessionId) {
        setCurrentSessionId(fetched[0].id);
      } else if (fetched.length === 0) {
        await createNewSession();
      }
      setIsLoadingSessions(false);
    };
    init();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <ChatContext.Provider
      value={{
        sessions,
        currentSessionId,
        setCurrentSessionId,
        createNewSession,
        deleteSession,
        refreshSessions,
        updateSessionTitle,
        isLoadingSessions,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
