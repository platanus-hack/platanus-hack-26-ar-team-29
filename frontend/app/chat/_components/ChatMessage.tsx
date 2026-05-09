import type { Message } from "../types";
import { TradeConfirmation } from "./TradeConfirmation";

export function ChatMessage({
  message,
  onConfirmTrade,
  onRejectTrade,
}: {
  message: Message;
  onConfirmTrade?: (messageId: string) => void;
  onRejectTrade?: (messageId: string) => void;
}) {
  const isUser = message.role === "user";

  if (message.trade) {
    return (
      <div className="flex justify-start">
        <div className="flex w-full max-w-[85%] flex-col gap-2">
          {message.content && (
            <div className="rounded-2xl rounded-bl-sm bg-zinc-200 px-4 py-2 text-sm whitespace-pre-wrap break-words text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100">
              {message.content}
            </div>
          )}
          <TradeConfirmation
            trade={message.trade.data}
            status={message.trade.status}
            onConfirm={() => onConfirmTrade?.(message.id)}
            onReject={() => onRejectTrade?.(message.id)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap break-words ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : "bg-zinc-200 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100 rounded-bl-sm"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
