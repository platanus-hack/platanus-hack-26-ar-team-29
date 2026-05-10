'use client';

import { useEffect, useState } from "react";
import { Sidebar } from "../_components/Sidebar";
import { PageHeader } from "../_components/PageHeader";
import { backendApi } from "../lib/backend/client";
import type { PositionRow } from "../lib/backend/types";

export default function InvestmentsPage() {
  const [positions, setPositions] = useState<PositionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    backendApi.getPositions().then((data) => {
      setPositions(data);
    }).catch((err) => {
      console.error(err);
      setError(err instanceof Error ? err.message : "No pudimos cargar inversiones.");
    }).finally(() => setLoading(false));
  }, []);

  const totalValue = positions.reduce((acc, pos) => acc + (pos.usd_value || 0), 0);
  const hasValuationData = positions.some((pos) => pos.usd_value !== null && pos.usd_value !== undefined);
  const hasPnlData = positions.some((pos) => pos.unrealized_pnl_usd !== null && pos.unrealized_pnl_usd !== undefined);
  const totalPnl = positions.reduce((acc, pos) => acc + (pos.unrealized_pnl_usd || 0), 0);
  const totalCost = positions.reduce((acc, pos) => acc + (pos.cost_basis_usd || 0), 0);
  const pnlPct = hasPnlData && totalCost > 0 ? (totalPnl / totalCost) * 100 : null;
  const largestAllocation = positions.reduce((max, pos) => {
    if (totalValue <= 0 || !pos.usd_value) return max;
    return Math.max(max, (pos.usd_value / totalValue) * 100);
  }, 0);
  const riskLabel = positions.length === 0
    ? "--"
    : !hasValuationData
      ? "n/d"
    : largestAllocation >= 50
      ? "Concentrado"
      : positions.length <= 2
        ? "Medio"
        : "Diversificado";

  const formatUsd = (value?: number | null) => {
    if (value === null || value === undefined) return "n/d";
    return `$${value.toLocaleString("es-AR", { maximumFractionDigits: 2 })}`;
  };

  const formatPct = (value?: number | null) => {
    if (value === null || value === undefined) return "n/d";
    return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
  };

  const summary = [
    { label: "Valor total USD", value: hasValuationData ? formatUsd(totalValue) : "n/d" },
    { label: "P&L no realizado", value: hasPnlData ? `${formatUsd(totalPnl)}${pnlPct !== null ? ` (${formatPct(pnlPct)})` : ""}` : "n/d" },
    { label: "Riesgo", value: riskLabel },
  ];

  return (
    <Sidebar>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader
          title="Inversiones"
          description="Resumen de tu cartera y posiciones principales."
        />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-background px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl space-y-6">
            <section className="grid gap-4 sm:grid-cols-3">
              {summary.map((item) => (
                <div
                  key={item.label}
                  className="rounded-3xl border border-line bg-card p-6 shadow-card transition-all duration-200 hover:border-accent/25 hover:shadow-card-hover"
                >
                  <div className="text-xs font-mono text-muted">{item.label}</div>
                  <div className="mt-3 text-2xl font-semibold tabular-nums text-foreground">{item.value}</div>
                </div>
              ))}
            </section>

            <section className="rounded-3xl border border-line bg-card shadow-card">
              <div className="border-b border-line px-6 py-5 text-sm font-semibold text-foreground flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>
                Posiciones destacadas
              </div>
              <div className="divide-y divide-line">
                {loading ? (
                  <div className="px-6 py-10 text-center text-muted">Cargando posiciones...</div>
                ) : error ? (
                  <div className="px-6 py-10 text-center text-muted">{error}</div>
                ) : positions.length === 0 ? (
                  <div className="px-6 py-10 text-center text-muted">No hay posiciones activas.</div>
                ) : (
                  positions.map((pos, idx) => {
                    const hasPositionValue = pos.usd_value !== null && pos.usd_value !== undefined;
                    const alloc = totalValue > 0 && hasPositionValue ? `${(pos.usd_value! / totalValue * 100).toFixed(1)}%` : "n/d";
                    const pnlClass = pos.unrealized_pnl_usd === null || pos.unrealized_pnl_usd === undefined
                      ? "text-muted"
                      : pos.unrealized_pnl_usd >= 0
                        ? "text-success"
                        : "text-red-500";
                    return (
                      <div key={idx} className="flex flex-col gap-3 px-6 py-5 sm:flex-row sm:items-center sm:justify-between transition-all duration-200 hover:bg-accent/5">
                        <div>
                          <div className="text-base font-medium text-foreground">{pos.symbol}</div>
                          <div className="text-xs font-mono text-muted mt-1">
                            <span className="text-accent">{pos.shares} shares</span> <span className="mx-1 opacity-50">·</span> {pos.provider}
                            {pos.current_price_usd ? <><span className="mx-1 opacity-50">·</span> {formatUsd(pos.current_price_usd)} c/u</> : null}
                          </div>
                        </div>
                        <div className="flex flex-wrap items-center gap-6 text-sm">
                          <div>
                            <div className="text-xs font-mono text-subdued mb-1">Alloc</div>
                            <div className="font-medium text-foreground">{alloc}</div>
                          </div>
                          <div>
                            <div className="text-xs font-mono text-subdued mb-1">Valor USD</div>
                            <div className="font-medium tabular-nums text-foreground">
                              {formatUsd(pos.usd_value)}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs font-mono text-subdued mb-1">P&L</div>
                            <div className={`font-medium tabular-nums ${pnlClass}`}>
                              {pos.unrealized_pnl_usd === null || pos.unrealized_pnl_usd === undefined
                                ? "n/d"
                                : `${formatUsd(pos.unrealized_pnl_usd)} (${formatPct(pos.pnl_percentage)})`}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </section>
          </div>
        </div>
      </div>
    </Sidebar>
  );
}
