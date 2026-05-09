import type { Trade } from "../types";

function formatAmount(n: number) {
  return n.toLocaleString("en-US", { maximumFractionDigits: 8 });
}

function formatUSD(n: number) {
  return `$${n.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function TradeSummary({ trade }: { trade: Trade }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-sm dark:border-zinc-700 dark:bg-zinc-900/60">
      <div className="flex items-center justify-between gap-3">
        <div className="flex flex-col">
          <span className="text-xs uppercase tracking-wide text-zinc-500">
            From
          </span>
          <span className="font-medium tabular-nums">
            {formatAmount(trade.fromAmount)} {trade.fromTicker}
          </span>
        </div>
        <span className="text-zinc-400">→</span>
        <div className="flex flex-col text-right">
          <span className="text-xs uppercase tracking-wide text-zinc-500">
            To
          </span>
          <span className="font-medium tabular-nums">
            {formatAmount(trade.toAmount)} {trade.toTicker}
          </span>
        </div>
      </div>
      <div className="mt-2 flex justify-end text-xs text-zinc-500 tabular-nums">
        ≈ {formatUSD(trade.valueUSD)}
      </div>
    </div>
  );
}
