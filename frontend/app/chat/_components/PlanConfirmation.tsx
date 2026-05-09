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
    <div className="space-y-3 rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm dark:border-zinc-700 dark:bg-zinc-950 sm:p-4 lg:p-5">
      <h3>Confirmá el plan</h3>
      <PlanSummary plan={plan} />
      {isActionable(plan.state) ? (
        <div className="grid grid-cols-1 gap-2 min-[380px]:grid-cols-2">
          <button
            type="button"
            onClick={onReject}
            disabled={isBusy}
            className="min-h-11 rounded-2xl border border-zinc-300 px-4 py-2 text-sm font-medium transition hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-700 dark:hover:bg-zinc-800 sm:rounded-full"
          >
            Rechazar
          </button>
          <button
            type="button"
            onClick={onApprove}
            disabled={isBusy}
            className="min-h-11 rounded-2xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50 sm:rounded-full"
          >
            Aprobar
          </button>
        </div>
      ) : null}
    </div>
  );
}
