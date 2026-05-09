import { AppShell } from "../_components/AppShell";
import { PageHeader } from "../_components/PageHeader";

const summary = [
  { label: "Valor total", value: "$12.480.550" },
  { label: "Rendimiento 30d", value: "+4,2%" },
  { label: "Riesgo", value: "Moderado" },
];

const positions = [
  {
    name: "S&P 500",
    symbol: "SPY",
    provider: "Wallbit",
    allocation: "38%",
    value: "$4.735.000",
    pnl: "+6,1%",
  },
  {
    name: "Ethereum",
    symbol: "ETH",
    provider: "Wallet",
    allocation: "22%",
    value: "$2.745.000",
    pnl: "+9,8%",
  },
  {
    name: "Renta fija USD",
    symbol: "T-Bills",
    provider: "Wallbit",
    allocation: "18%",
    value: "$2.246.000",
    pnl: "+1,2%",
  },
  {
    name: "CEDEARs Latam",
    symbol: "MELI + GLOB",
    provider: "Wallbit",
    allocation: "14%",
    value: "$1.746.000",
    pnl: "+3,4%",
  },
  {
    name: "Stablecoins",
    symbol: "USDC",
    provider: "Wallet",
    allocation: "8%",
    value: "$1.008.550",
    pnl: "+0,1%",
  },
];

export default function InvestmentsPage() {
  return (
    <AppShell>
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
                {positions.map((pos) => (
                  <div key={pos.name} className="flex flex-col gap-3 px-6 py-5 sm:flex-row sm:items-center sm:justify-between transition-all duration-200 hover:bg-accent/5">
                    <div>
                      <div className="text-base font-medium text-foreground">{pos.name}</div>
                      <div className="text-xs font-mono text-muted mt-1">
                        <span className="text-accent">{pos.symbol}</span> <span className="mx-1 opacity-50">·</span> {pos.provider}
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-6 text-sm">
                      <div>
                        <div className="text-xs font-mono text-subdued mb-1">Alloc</div>
                        <div className="font-medium text-foreground">{pos.allocation}</div>
                      </div>
                      <div>
                        <div className="text-xs font-mono text-subdued mb-1">Valor</div>
                        <div className="font-medium tabular-nums text-foreground">{pos.value}</div>
                      </div>
                      <div>
                        <div className="text-xs font-mono text-subdued mb-1">P&L</div>
                        <div className="font-medium tabular-nums text-success">{pos.pnl}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
