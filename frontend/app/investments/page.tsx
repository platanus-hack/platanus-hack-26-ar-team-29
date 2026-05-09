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
        <div className="flex-1 overflow-y-auto overscroll-contain bg-[#050505] px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl space-y-6">
            <section className="grid gap-4 sm:grid-cols-3">
              {summary.map((item) => (
                <div
                  key={item.label}
                  className="rounded-3xl border border-[#1A1A1A] bg-[#080C0D] p-6 shadow-[0_0_24px_rgba(56,217,198,0.03)] transition-all duration-200 hover:border-[#38D9C6]/25 hover:shadow-[0_0_30px_rgba(56,217,198,0.06)]"
                >
                  <div className="text-xs font-mono text-[#A8B3C2]">{item.label}</div>
                  <div className="mt-3 text-2xl font-semibold tabular-nums text-[#F4F8FB]">{item.value}</div>
                </div>
              ))}
            </section>

            <section className="rounded-3xl border border-[#1A1A1A] bg-[#080C0D] shadow-[0_0_24px_rgba(56,217,198,0.03)]">
              <div className="border-b border-[#1A1A1A] px-6 py-5 text-sm font-semibold text-[#F4F8FB] flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-[#38D9C6]"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>
                Posiciones destacadas
              </div>
              <div className="divide-y divide-[#1A1A1A]">
                {positions.map((pos) => (
                  <div key={pos.name} className="flex flex-col gap-3 px-6 py-5 sm:flex-row sm:items-center sm:justify-between transition-all duration-200 hover:bg-[#38D9C6]/5">
                    <div>
                      <div className="text-base font-medium text-[#F4F8FB]">{pos.name}</div>
                      <div className="text-xs font-mono text-[#A8B3C2] mt-1">
                        <span className="text-[#38D9C6]">{pos.symbol}</span> <span className="mx-1 opacity-50">·</span> {pos.provider}
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-6 text-sm">
                      <div>
                        <div className="text-xs font-mono text-[#6B7788] mb-1">Alloc</div>
                        <div className="font-medium text-[#F4F8FB]">{pos.allocation}</div>
                      </div>
                      <div>
                        <div className="text-xs font-mono text-[#6B7788] mb-1">Valor</div>
                        <div className="font-medium tabular-nums text-[#F4F8FB]">{pos.value}</div>
                      </div>
                      <div>
                        <div className="text-xs font-mono text-[#6B7788] mb-1">P&L</div>
                        <div className="font-medium tabular-nums text-[#3EE98A]">{pos.pnl}</div>
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
