import { useEffect, useRef } from "react";
import type { Message } from "../types";
import { ChatMessage } from "./ChatMessage";

export function ChatThread({
  messages,
  isTyping,
  onApprovePlan,
  onRejectPlan,
  busyPlanId,
}: {
  messages: Message[];
  isTyping: boolean;
  onApprovePlan?: (planId: string) => void;
  onRejectPlan?: (planId: string) => void;
  busyPlanId?: string | null;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div ref={ref} className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
      <div className="space-y-5 bg-zinc-50 px-4 py-5 dark:bg-zinc-950 sm:px-6 sm:py-7 lg:px-12">
        {messages.length === 0 && !isTyping && (
          <div className="mx-auto flex min-h-full max-w-sm flex-col items-center justify-center px-4 py-10 text-center">
            <div className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-900 dark:ring-zinc-800">
              <h2>Hablá con OpenFi</h2>
              <p className="mt-2">
                Probá con: “comprá 7 usd de apple” para ver una propuesta de plan.
              </p>
            </div>
          </div>
        )}
      {messages.map((m) => (
        <ChatMessage
          key={m.id}
          message={m}
          onApprovePlan={onApprovePlan}
          onRejectPlan={onRejectPlan}
          busyPlanId={busyPlanId}
        />
      ))}
      {isTyping && (
        <div className="flex justify-start">
          <div className="rounded-2xl rounded-bl-sm bg-white px-4 py-2 text-sm text-zinc-500 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-900 dark:text-zinc-400 dark:ring-zinc-800">
            <span className="inline-flex gap-1">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:300ms]" />
            </span>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
