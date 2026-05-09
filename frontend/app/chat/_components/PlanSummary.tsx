import type { TradePlan } from "../../lib/backend/types";

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

export function PlanSummary({ plan }: { plan: TradePlan }) {
  return (
    <div className="space-y-3 rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-sm dark:border-zinc-700 dark:bg-zinc-900/60 sm:p-4">
      <div className="flex flex-col gap-2 min-[360px]:flex-row min-[360px]:items-center min-[360px]:justify-between min-[360px]:gap-3">
        <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">
          Plan #{plan.id.slice(0, 8)}
        </span>
        <span className="w-fit rounded-full bg-zinc-200 px-2 py-0.5 text-xs font-medium text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
          {stateLabel(plan.state)}
        </span>
      </div>

      {plan.total_estimated_usd != null && (
        <div className="text-2xl font-semibold tabular-nums sm:text-3xl">
          {formatUSD(plan.total_estimated_usd)}
        </div>
      )}

      <ol className="space-y-2">
        {plan.steps.map((step) => (
          <li key={step.id} className="rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex flex-col gap-2 min-[430px]:flex-row min-[430px]:items-start min-[430px]:justify-between min-[430px]:gap-3">
              <div className="min-w-0">
                <div className="font-medium">
                  {step.human_description_es || step.human_description_en || step.tool_name}
                </div>
                <div className="mt-1 text-xs text-zinc-500">
                  Paso {step.ordinal} · {step.tool_name}
                  {step.estimated_usd != null ? ` · ${formatUSD(step.estimated_usd)}` : ""}
                </div>
                {step.result_summary && (
                  <div className="mt-1 text-xs text-zinc-500">{step.result_summary}</div>
                )}
              </div>
              <span className="w-fit shrink-0 rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                {stateLabel(step.state)}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
