import type { TradePlan } from "../../lib/backend/types";
import { PlanSummary } from "./PlanSummary";

function isActionable(state: string) {
  return state === "pending_approval";
}

export function PlanConfirmation({
  plan,
  isBusy,
  onApprove,
  onReject,
}: {
  plan: TradePlan;
  isBusy?: boolean;
  onApprove: () => void;
  onReject: () => void;
}) {
  return (
    <div className="space-y-4 rounded-3xl border border-[#1A1A1A] bg-[#080C0D] p-5 shadow-[0_0_24px_rgba(56,217,198,0.03)] lg:p-7">
      <h3 className="flex items-center gap-2 text-lg font-semibold text-[#F4F8FB]">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[#38D9C6]"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        Revisar Transacción
      </h3>
      <PlanSummary plan={plan} />
      {isActionable(plan.state) ? (
        <div className="grid grid-cols-1 gap-3 min-[380px]:grid-cols-2 pt-2">
          <button
            type="button"
            onClick={onReject}
            disabled={isBusy}
            className="min-h-12 rounded-xl border border-[#1A1A1A] bg-[#050505] px-4 py-2 text-sm font-medium text-[#A8B3C2] transition-all duration-200 hover:bg-[#1A1A1A]/50 hover:text-[#F4F8FB] disabled:cursor-not-allowed disabled:opacity-50"
          >
            Rechazar
          </button>
          <button
            type="button"
            onClick={onApprove}
            disabled={isBusy}
            className="min-h-12 rounded-xl border border-[#38D9C6]/30 bg-[#38D9C6]/10 px-4 py-2 text-sm font-bold text-[#38D9C6] transition-all duration-200 hover:bg-[#38D9C6] hover:text-[#050505] hover:shadow-[0_0_20px_rgba(56,217,198,0.3)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            Aprobar
          </button>
        </div>
      ) : null}
    </div>
  );
}
