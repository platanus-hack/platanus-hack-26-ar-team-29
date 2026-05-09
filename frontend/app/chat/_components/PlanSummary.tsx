import type { TradePlan, TradePlanStep } from "../../lib/backend/types";

function formatUSD(n?: number | null) {
  if (n == null) return null;
  return `$${n.toLocaleString("es-AR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function stateLabel(state: string) {
  const labels: Record<string, string> = {
    pending: "Pendiente",
    pending_approval: "Pendiente de aprobación",
    approved: "Aprobado",
    executing: "Ejecutando",
    ok: "OK",
    failed: "Falló",
    completed: "Completado",
    partially_failed: "Parcialmente fallido",
    rejected: "Rechazado",
    expired: "Vencido",
  };
  return labels[state] ?? state;
}

const TRADE_TOOL_NAMES = new Set(["mcp__wallbit__create_trade", "create_trade"]);

function isTradeStep(step: TradePlanStep) {
  return TRADE_TOOL_NAMES.has(step.tool_name);
}

function TradeStepBody({
  args,
  unitPriceUsd,
}: {
  args: Record<string, unknown>;
  unitPriceUsd?: number | null;
}) {
  const symbol = String(args.symbol ?? "").toUpperCase();
  const direction = String(args.direction ?? "").toUpperCase();
  const orderType = String(args.order_type ?? "").toUpperCase();
  const currency = String(args.currency ?? "USD").toUpperCase();
  const shares = typeof args.shares === "number" ? args.shares : null;
  const amount = typeof args.amount === "number" ? args.amount : null;

  const actionVerb =
    direction === "BUY" ? "Comprar" : direction === "SELL" ? "Vender" : direction || "Operar";
  const directionTone =
    direction === "BUY" ? "text-accent" : direction === "SELL" ? "text-rose-400" : "text-foreground";
  const orderLabel =
    orderType === "MARKET"
      ? "Orden de mercado"
      : orderType === "LIMIT"
        ? "Orden límite"
        : orderType;

  const quantityNode =
    shares != null ? (
      <span className="text-foreground">
        {shares} {shares === 1 ? "acción" : "acciones"}
      </span>
    ) : amount != null ? (
      <span className="text-foreground">{formatUSD(amount)}</span>
    ) : null;

  return (
    <div className="space-y-2.5">
      <div className="text-xl font-semibold leading-snug">
        <span className={directionTone}>{actionVerb}</span>
        {quantityNode && <span> {quantityNode}</span>}
        {symbol && (
          <>
            <span className="text-muted"> de </span>
            <span className="font-mono text-foreground">{symbol}</span>
          </>
        )}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {orderLabel && (
          <span className="rounded-full border border-line bg-background px-2 py-0.5 text-xs text-muted">
            {orderLabel}
          </span>
        )}
        {currency && (
          <span className="rounded-full border border-line bg-background px-2 py-0.5 text-xs text-muted">
            {currency}
          </span>
        )}
      </div>
      {unitPriceUsd != null && (
        <dl className="grid grid-cols-[max-content_1fr] gap-x-3 gap-y-1 pt-1 text-xs">
          <dt className="text-muted">Precio actual</dt>
          <dd className="font-mono tabular-nums text-foreground">
            {formatUSD(unitPriceUsd)} <span className="text-muted">/ acción</span>
          </dd>
          {shares != null && (
            <>
              <dt className="text-muted">Cantidad</dt>
              <dd className="font-mono tabular-nums text-foreground">
                {shares} {shares === 1 ? "acción" : "acciones"}
              </dd>
            </>
          )}
        </dl>
      )}
    </div>
  );
}

export function PlanSummary({ plan }: { plan: TradePlan }) {
  return (
    <div className="space-y-3 rounded-2xl border border-line bg-background p-4 text-sm sm:p-5">
      <div className="flex flex-col gap-2 min-[360px]:flex-row min-[360px]:items-center min-[360px]:justify-between min-[360px]:gap-3">
        <span className="text-xs font-mono font-medium tracking-wide text-muted">
          TX-PLAN-{plan.id.slice(0, 8)}
        </span>
        <span className="w-fit rounded-full border border-line bg-card px-2 py-0.5 text-xs font-medium text-foreground">
          {stateLabel(plan.state)}
        </span>
      </div>

      {plan.total_estimated_usd != null && (
        <div className="text-3xl font-mono text-accent font-semibold tabular-nums tracking-tight">
          {formatUSD(plan.total_estimated_usd)}
        </div>
      )}

      <ol className="space-y-2 mt-4">
        {plan.steps.map((step) => {
          const trade = isTradeStep(step);
          return (
            <li
              key={step.id}
              className="rounded-xl border border-line bg-card p-3 transition-all duration-200 hover:border-accent/20 hover:bg-accent/5 sm:p-4"
            >
              <div className="flex flex-col gap-3 min-[430px]:flex-row min-[430px]:items-start min-[430px]:justify-between min-[430px]:gap-3">
                <div className="min-w-0 flex-1">
                  {trade ? (
                    <TradeStepBody
                      args={step.args || {}}
                      unitPriceUsd={plan.estimated_unit_price_usd}
                    />
                  ) : (
                    <>
                      <div className="font-medium text-foreground">
                        {step.human_description_es ||
                          step.human_description_en ||
                          step.tool_name}
                      </div>
                      <div className="mt-1 text-xs text-subdued">
                        Step {step.ordinal} ·{" "}
                        <span className="font-mono text-muted">{step.tool_name}</span>
                        {step.estimated_usd != null
                          ? ` · ${formatUSD(step.estimated_usd)}`
                          : ""}
                      </div>
                    </>
                  )}
                  {trade && step.estimated_usd != null && (
                    <div className="mt-2 text-xs text-muted">
                      Costo estimado:{" "}
                      <span className="text-foreground">{formatUSD(step.estimated_usd)}</span>
                    </div>
                  )}
                  {step.result_summary && (
                    <div className="mt-2 text-xs text-muted">{step.result_summary}</div>
                  )}
                </div>
                <span className="w-fit shrink-0 rounded-full bg-background border border-line px-2 py-0.5 text-xs text-muted">
                  {stateLabel(step.state)}
                </span>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
