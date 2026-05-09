import type { TradePlan } from "../../lib/backend/types";
import { PlanSummary } from "./PlanSummary";
import { Button } from "../../_components/Button";

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
    <div className="space-y-4 rounded-3xl border border-line bg-card p-5 shadow-card lg:p-7">
      <h3 className="flex items-center gap-2 text-lg font-semibold text-foreground">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        Revisar Transacción
      </h3>
      <PlanSummary plan={plan} />
      {isActionable(plan.state) ? (
        <div className="grid grid-cols-1 gap-3 min-[380px]:grid-cols-2 pt-2">
          <Button
            type="button"
            onClick={onReject}
            disabled={isBusy}
            variant="outline"
            className="min-h-12"
          >
            Rechazar
          </Button>
          <Button
            type="button"
            onClick={onApprove}
            disabled={isBusy}
            variant="primary"
            className="min-h-12"
          >
            Aprobar
          </Button>
        </div>
      ) : null}
    </div>
  );
}
