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
    <div className="space-y-3 rounded-2xl border border-[#1A1A1A] bg-[#050505] p-4 text-sm sm:p-5">
      <div className="flex flex-col gap-2 min-[360px]:flex-row min-[360px]:items-center min-[360px]:justify-between min-[360px]:gap-3">
        <span className="text-xs font-mono font-medium tracking-wide text-[#A8B3C2]">
          TX-PLAN-{plan.id.slice(0, 8)}
        </span>
        <span className="w-fit rounded-full border border-[#1A1A1A] bg-[#080C0D] px-2 py-0.5 text-xs font-medium text-[#F4F8FB]">
          {stateLabel(plan.state)}
        </span>
      </div>

      {plan.total_estimated_usd != null && (
        <div className="text-3xl font-mono text-[#38D9C6] font-semibold tabular-nums tracking-tight">
          {formatUSD(plan.total_estimated_usd)}
        </div>
      )}

      <ol className="space-y-2 mt-4">
        {plan.steps.map((step) => (
          <li key={step.id} className="rounded-xl border border-[#1A1A1A] bg-[#080C0D] p-3 transition-all duration-200 hover:border-[#38D9C6]/20 hover:bg-[#38D9C6]/5">
            <div className="flex flex-col gap-2 min-[430px]:flex-row min-[430px]:items-start min-[430px]:justify-between min-[430px]:gap-3">
              <div className="min-w-0">
                <div className="font-medium text-[#F4F8FB]">
                  {step.human_description_es || step.human_description_en || step.tool_name}
                </div>
                <div className="mt-1 text-xs text-[#6B7788]">
                  Step {step.ordinal} · <span className="font-mono text-[#A8B3C2]">{step.tool_name}</span>
                  {step.estimated_usd != null ? ` · ${formatUSD(step.estimated_usd)}` : ""}
                </div>
                {step.result_summary && (
                  <div className="mt-1 text-xs text-[#A8B3C2]">{step.result_summary}</div>
                )}
              </div>
              <span className="w-fit shrink-0 rounded-full bg-[#050505] border border-[#1A1A1A] px-2 py-0.5 text-xs text-[#A8B3C2]">
                {stateLabel(step.state)}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
