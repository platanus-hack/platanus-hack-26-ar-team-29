import type { Message } from "../types";
import { PlanConfirmation } from "./PlanConfirmation";

export function ChatMessage({
  message,
  onApprovePlan,
  onRejectPlan,
  busyPlanId,
}: {
  message: Message;
  onApprovePlan?: (planId: string) => void;
  onRejectPlan?: (planId: string) => void;
  busyPlanId?: string | null;
}) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (message.plan) {
    return (
      <div className="flex justify-start">
        <div className="flex w-full flex-col gap-2 sm:max-w-[88%] md:max-w-[82%]">
          {message.content && (
            <div className="rounded-2xl rounded-bl-sm bg-white px-4 py-2 text-sm whitespace-pre-wrap break-words text-zinc-900 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-900 dark:text-zinc-100 dark:ring-zinc-800">
              {message.content}
            </div>
          )}
          <PlanConfirmation
            plan={message.plan}
            isBusy={busyPlanId === message.plan.id}
            onApprove={() => onApprovePlan?.(message.plan!.id)}
            onReject={() => onRejectPlan?.(message.plan!.id)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[88%] rounded-2xl px-3.5 py-2.5 text-sm leading-6 whitespace-pre-wrap break-words shadow-sm sm:max-w-[78%] sm:px-4 sm:py-2 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : isSystem
              ? "bg-amber-50 text-amber-900 ring-1 ring-amber-200 dark:bg-amber-950/30 dark:text-amber-100 dark:ring-amber-900 rounded-bl-sm"
              : "bg-white text-zinc-900 ring-1 ring-zinc-200 dark:bg-zinc-900 dark:text-zinc-100 dark:ring-zinc-800 rounded-bl-sm"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
