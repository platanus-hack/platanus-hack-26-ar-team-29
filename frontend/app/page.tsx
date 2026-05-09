"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AppShell } from "./_components/AppShell";
import { ChatInput } from "./chat/_components/ChatInput";
import { ChatThread } from "./chat/_components/ChatThread";
import type { Message } from "./chat/types";
import { BackendApiError, backendApi } from "./lib/backend/client";
import { openSessionWebSocket, type BackendWsSubscription } from "./lib/backend/ws";
import type { BackendWsFrame, ChatMessageDto, TradePlan } from "./lib/backend/types";

function makeId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function dtoToMessage(dto: ChatMessageDto, plan?: TradePlan): Message {
  return {
    id: dto.id,
    role: dto.role,
    content: dto.content,
    createdAt: Date.parse(dto.created_at) || Date.now(),
    kind: dto.kind === "plan_proposal" ? "plan_proposal" : "text",
    planId: dto.plan_id,
    plan,
  };
}

function errorText(err: unknown) {
  if (err instanceof BackendApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Ocurrió un error inesperado.";
}

function sortMessages(messages: Message[]) {
  return [...messages].sort((a, b) => a.createdAt - b.createdAt);
}

export default function ChatPage() {
  const wsRef = useRef<BackendWsSubscription | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isBooting, setIsBooting] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const [busyPlanId, setBusyPlanId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);


  const upsertMessage = useCallback((message: Message) => {
    setMessages((prev) => {
      const withoutSame = prev.filter((m) => m.id !== message.id);
      return sortMessages([...withoutSame, message]);
    });
  }, []);

  const updatePlan = useCallback((planId: string, updater: (plan: TradePlan) => TradePlan) => {
    setMessages((prev) =>
      prev.map((message) =>
        message.plan?.id === planId ? { ...message, plan: updater(message.plan) } : message,
      ),
    );
  }, []);

  const appendSystemMessage = useCallback((content: string) => {
    upsertMessage({
      id: makeId(),
      role: "system",
      content,
      createdAt: Date.now(),
      kind: "error",
    });
  }, [upsertMessage]);

  const handleWsFrame = useCallback(
    (frame: BackendWsFrame) => {
      if (frame.type === "subscribed") {
        return;
        return;
      }

      if (frame.type === "ping") {
        wsRef.current?.sendPing();
        return;
      }

      if (frame.type === "chat_token") {
        setIsTyping(true);
        setMessages((prev) => {
          const streamId = `stream-${frame.turn_id}`;
          const existing = prev.find((m) => m.id === streamId);
          const nextMessage: Message = existing
            ? { ...existing, content: existing.content + frame.delta }
            : {
                id: streamId,
                role: "assistant",
                content: frame.delta,
                createdAt: Date.now(),
                kind: "stream",
              };
          return sortMessages([...prev.filter((m) => m.id !== streamId), nextMessage]);
        });
        return;
      }

      if (frame.type === "chat_message") {
        setMessages((prev) => {
          const withoutStreams = prev.filter((m) => !m.id.startsWith("stream-"));
          return sortMessages([...withoutStreams.filter((m) => m.id !== frame.message.id), dtoToMessage(frame.message)]);
        });
        return;
      }

      if (frame.type === "plan_proposed") {
        upsertMessage({
          id: `plan-${frame.plan_id}`,
          role: "assistant",
          content: "",
          createdAt: Date.now(),
          kind: "plan_proposal",
          planId: frame.plan_id,
          plan: frame.plan,
        });
        return;
      }

      if (frame.type === "plan_update") {
        updatePlan(frame.plan_id, (plan) => ({
          ...plan,
          state: frame.step_id ? plan.state : frame.state,
          steps: frame.step_id
            ? plan.steps.map((step) =>
                step.id === frame.step_id
                  ? {
                      ...step,
                      state: frame.state,
                      result_summary: frame.summary || frame.error || step.result_summary,
                    }
                  : step,
              )
            : plan.steps,
        }));
        return;
      }

      if (frame.type === "turn_complete") {
        setIsTyping(false);
        setMessages((prev) => prev.filter((m) => !m.id.startsWith("stream-")));
        return;
      }

      if (frame.type === "error") {
        setIsTyping(false);
        appendSystemMessage(frame.message_es || frame.message_en || frame.code);
      }
    },
    [appendSystemMessage, updatePlan, upsertMessage],
  );

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      setIsBooting(true);
      setError(null);
      try {
        const sessions = await backendApi.listChatSessions();
        const session = sessions[0] ?? (await backendApi.createChatSession({ title: "Demo" }));
        if (cancelled) return;

        setSessionId(session.id);
        const rawMessages = await backendApi.listChatMessages(session.id);
        const hydrated = await Promise.all(
          rawMessages.map(async (message) => {
            if (message.kind === "plan_proposal" && message.plan_id) {
              try {
                return dtoToMessage(message, await backendApi.getPlan(message.plan_id));
              } catch {
                return dtoToMessage(message);
              }
            }
            return dtoToMessage(message);
          }),
        );
        if (!cancelled) setMessages(sortMessages(hydrated));
      } catch (err) {
        if (!cancelled) setError(errorText(err));
      } finally {
        if (!cancelled) setIsBooting(false);
      }
    }

    boot();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!sessionId) return;

    wsRef.current?.close();
    wsRef.current = openSessionWebSocket({
      sessionId,
      onFrame: handleWsFrame,
      onClose: () => undefined,
      onError: () => setError("No pudimos conectar el WebSocket del chat."),
    });

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [handleWsFrame, sessionId]);

  async function handleSend(text: string) {
    if (!sessionId) return;
    const userMsg: Message = {
      id: makeId(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };
    upsertMessage(userMsg);
    setIsTyping(true);
    setError(null);

    try {
      await backendApi.sendChatMessage(sessionId, text);
    } catch (err) {
      appendSystemMessage(errorText(err));
      setIsTyping(false);
    }
  }

  async function approvePlan(planId: string) {
    setBusyPlanId(planId);
    setError(null);
    updatePlan(planId, (plan) => ({ ...plan, state: "approved" }));
    try {
      await backendApi.approvePlan(planId);
    } catch (err) {
      appendSystemMessage(errorText(err));
      try {
        const fresh = await backendApi.getPlan(planId);
        updatePlan(planId, () => fresh);
      } catch {
        updatePlan(planId, (plan) => ({ ...plan, state: "pending_approval" }));
      }
    } finally {
      setBusyPlanId(null);
    }
  }

  async function rejectPlan(planId: string) {
    setBusyPlanId(planId);
    setError(null);
    updatePlan(planId, (plan) => ({ ...plan, state: "rejected" }));
    try {
      await backendApi.rejectPlan(planId, "Rechazado desde frontend");
    } catch (err) {
      appendSystemMessage(errorText(err));
      try {
        const fresh = await backendApi.getPlan(planId);
        updatePlan(planId, () => fresh);
      } catch {
        updatePlan(planId, (plan) => ({ ...plan, state: "pending_approval" }));
      }
    } finally {
      setBusyPlanId(null);
    }
  }

  return (
    <AppShell>
      <div className="flex h-[100dvh] w-full flex-col border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950 md:h-full md:border-l">
        <header className="shrink-0 border-b border-zinc-200 bg-white/95 px-4 pb-3 pt-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/95 sm:px-6 sm:py-5 lg:px-10">
          <div className="flex flex-col gap-2 min-[380px]:flex-row min-[380px]:items-start min-[380px]:justify-between">
            <div className="min-w-0">
              <h1 className="truncate">OpenFi Chat</h1>
            </div>
          </div>
          {error && (
            <div className="mt-2 rounded-xl bg-red-50 px-3 py-2 text-sm leading-6 text-red-700 dark:bg-red-950/30 dark:text-red-200">
              {error}
            </div>
          )}
        </header>
        <ChatThread
          messages={messages}
          isTyping={isTyping || isBooting}
          onApprovePlan={approvePlan}
          onRejectPlan={rejectPlan}
          busyPlanId={busyPlanId}
        />
        <ChatInput onSend={handleSend} disabled={isTyping || isBooting || !sessionId} />
      </div>
    </AppShell>
  );
}
