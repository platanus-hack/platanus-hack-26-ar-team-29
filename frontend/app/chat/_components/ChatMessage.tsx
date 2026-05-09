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
        <div className="flex w-full flex-col gap-3 sm:max-w-[88%] lg:max-w-[78%]">
          {message.content && (
            <div className="rounded-2xl rounded-bl-sm border border-[#1A1A1A] bg-[#080C0D] px-5 py-3 text-sm whitespace-pre-wrap break-words text-[#F4F8FB] shadow-sm">
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
          className={`max-w-[96%] rounded-2xl px-5 py-3.5 text-sm whitespace-pre-wrap break-words shadow-sm sm:max-w-[86%] md:max-w-[74%] lg:max-w-[68%] xl:max-w-[62%] ${
            isUser
              ? "bg-[#38D9C6]/10 text-[#F4F8FB] border border-[#38D9C6]/30 rounded-br-sm shadow-[0_0_15px_rgba(56,217,198,0.08)]"
              : isSystem
                ? "bg-[#F5B84B]/10 text-[#F5B84B] border border-[#F5B84B]/20 rounded-bl-sm"
                : "bg-[#080C0D] text-[#F4F8FB] border border-[#1A1A1A] rounded-bl-sm"
          }`}
        >
          {message.content}
        </div>
    </div>
  );
}
