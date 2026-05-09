import type { Trade, TradeStatus } from "../types";
import { TradeSummary } from "./TradeSummary";

export function TradeConfirmation({
  trade,
  status = "pending",
  onConfirm,
  onReject,
}: {
  trade: Trade;
  status?: TradeStatus;
  onConfirm: () => void;
  onReject: () => void;
}) {
  return (
    <div className="space-y-3 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-700 dark:bg-zinc-950">
      <div className="text-sm font-semibold">Confirm trade</div>
      <TradeSummary trade={trade} />
      {status === "pending" ? (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onReject}
            className="flex-1 rounded-full border border-zinc-300 px-4 py-2 text-sm font-medium transition hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-800"
          >
            Reject
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="flex-1 rounded-full bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
          >
            Confirm
          </button>
        </div>
      ) : (
        <div
          className={`text-sm font-medium ${
            status === "confirmed"
              ? "text-emerald-600 dark:text-emerald-400"
              : "text-zinc-500"
          }`}
        >
          {status === "confirmed" ? "✓ Confirmed" : "✕ Rejected"}
        </div>
      )}
    </div>
  );
}
