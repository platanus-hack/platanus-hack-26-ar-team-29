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
        <div className="flex-1 space-y-6 bg-zinc-50 px-4 py-6 dark:bg-zinc-950 sm:px-6 lg:px-10">
          <section className="grid gap-4 sm:grid-cols-3">
            {summary.map((item) => (
              <div
                key={item.label}
                className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="text-xs text-zinc-500">{item.label}</div>
                <div className="mt-2 text-lg font-semibold">{item.value}</div>
              </div>
            ))}
          </section>

          <section className="rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <div className="border-b border-zinc-200 px-4 py-3 text-sm font-semibold dark:border-zinc-800">
              Posiciones destacadas
            </div>
            <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {positions.map((pos) => (
                <div key={pos.name} className="flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="text-base font-medium">{pos.name}</div>
                    <div className="text-xs text-zinc-500">
                      {pos.symbol} · {pos.provider}
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-6 text-sm">
                    <div>
                      <div className="text-xs text-zinc-500">Alloc</div>
                      <div className="font-medium">{pos.allocation}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Valor</div>
                      <div className="font-medium">{pos.value}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">P&L</div>
                      <div className="font-medium text-emerald-600">{pos.pnl}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
