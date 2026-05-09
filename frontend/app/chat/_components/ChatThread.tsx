import { useEffect, useRef } from "react";
import type { Message } from "../types";
import { ChatMessage } from "./ChatMessage";

export function ChatThread({
  messages,
  isTyping,
  onConfirmTrade,
  onRejectTrade,
}: {
  messages: Message[];
  isTyping: boolean;
  onConfirmTrade?: (messageId: string) => void;
  onRejectTrade?: (messageId: string) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div ref={ref} className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-6">
      {messages.map((m) => (
        <ChatMessage
          key={m.id}
          message={m}
          onConfirmTrade={onConfirmTrade}
          onRejectTrade={onRejectTrade}
        />
      ))}
      {isTyping && (
        <div className="flex justify-start">
          <div className="rounded-2xl rounded-bl-sm bg-zinc-200 px-4 py-2 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
            <span className="inline-flex gap-1">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current [animation-delay:300ms]" />
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
