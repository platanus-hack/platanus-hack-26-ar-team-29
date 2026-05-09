import { AppShell } from "../_components/AppShell";
import { PageHeader } from "../_components/PageHeader";

const balances = [
  {
    provider: "Wallbit",
    account: "Cuenta USD",
    currency: "USD",
    available: "$2.450.000",
    updated: "hace 2 min",
  },
  {
    provider: "Wallbit",
    account: "Inversiones",
    currency: "USD",
    available: "$1.125.000",
    updated: "hace 2 min",
  },
  {
    provider: "Wallet",
    account: "USDC",
    currency: "USDC",
    available: "$890.000",
    updated: "hace 1 min",
  },
  {
    provider: "Wallet",
    account: "ETH",
    currency: "ETH",
    available: "1.9 ETH",
    updated: "hace 1 min",
  },
];

export default function BalancesPage() {
  return (
    <AppShell>
      <div className="flex min-h-0 flex-1 flex-col">
        <PageHeader title="Balances" description="Saldos por proveedor y moneda." />
        <div className="flex-1 overflow-y-auto overscroll-contain bg-[#050505] px-4 py-6 sm:px-6 lg:px-10">
          <div className="mx-auto max-w-5xl grid gap-4 sm:grid-cols-2">
            {balances.map((item) => (
              <div
                key={`${item.provider}-${item.account}`}
                className="rounded-3xl border border-[#1A1A1A] bg-[#080C0D] p-6 shadow-[0_0_24px_rgba(56,217,198,0.03)] transition-all duration-200 hover:border-[#38D9C6]/25 hover:shadow-[0_0_30px_rgba(56,217,198,0.06)]"
              >
                <div className="flex items-center justify-between text-xs text-[#A8B3C2] font-mono">
                  <span>
                    {item.provider} <span className="mx-1 text-[#38D9C6]/50">·</span> {item.account}
                  </span>
                  <span>{item.updated}</span>
                </div>
                <div className="mt-3 text-2xl font-semibold tabular-nums text-[#F4F8FB]">{item.available}</div>
                <div className="text-xs text-[#6B7788] font-mono">{item.currency}</div>
                <button
                  type="button"
                  className="mt-5 w-full rounded-xl border border-[#38D9C6]/25 bg-[#050505] px-3 py-2 text-xs font-medium text-[#A8B3C2] transition-all duration-200 hover:bg-[#38D9C6]/10 hover:text-[#F4F8FB] hover:border-[#38D9C6]/50 active:scale-[0.98]"
                >
                  Pedir a OpenFi
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
